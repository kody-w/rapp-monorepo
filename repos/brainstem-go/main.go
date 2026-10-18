package main

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"time"
)

const (
	kernelVersion       = "0.6.16"
	maxToolRounds       = 3
	emptyResponsePrompt = "I couldn't finish that within the available tool steps. Try rephrasing, or breaking it into smaller steps."
)

type config struct {
	port         string
	tokenURL     string
	modelURL     string
	model        string
	agentsPath   string
	python       string
	agentShim    string
	agents       []agentDefinition
	agentsByName map[string]agentDefinition
}

type agentDefinition struct {
	Name     string         `json:"name"`
	Metadata map[string]any `json:"metadata"`
}

type tokenResponse struct {
	Token     string `json:"token"`
	ExpiresAt int64  `json:"expires_at"`
	Endpoints struct {
		API string `json:"api"`
	} `json:"endpoints"`
}

type modelResponse struct {
	Model   string `json:"model"`
	Choices []struct {
		Message modelMessage `json:"message"`
	} `json:"choices"`
}

type modelMessage struct {
	Role      string     `json:"role"`
	Content   *string    `json:"content"`
	ToolCalls []toolCall `json:"tool_calls"`
}

type toolCall struct {
	ID       string `json:"id"`
	Type     string `json:"type"`
	Function struct {
		Name      string `json:"name"`
		Arguments string `json:"arguments"`
	} `json:"function"`
}

type shimResult struct {
	OK     bool   `json:"ok"`
	Result string `json:"result"`
	Error  string `json:"error"`
}

func main() {
	cfg, err := loadConfig()
	if err != nil {
		log.Fatal(err)
	}

	mux := http.NewServeMux()
	mux.HandleFunc("/health", cfg.handleHealth)
	mux.HandleFunc("/version", cfg.handleVersion)
	mux.HandleFunc("/chat", cfg.handleChat)

	server := &http.Server{
		Addr:              "127.0.0.1:" + cfg.port,
		Handler:           mux,
		ReadHeaderTimeout: 5 * time.Second,
	}
	log.Fatal(server.ListenAndServe())
}

func loadConfig() (*config, error) {
	port := strings.TrimSpace(os.Getenv("PORT"))
	if port == "" {
		return nil, errors.New("PORT is required")
	}
	if _, err := strconv.Atoi(port); err != nil {
		return nil, fmt.Errorf("invalid PORT: %w", err)
	}

	executable, err := os.Executable()
	if err != nil {
		return nil, fmt.Errorf("locate executable: %w", err)
	}
	shim := filepath.Join(filepath.Dir(executable), "agent_shim.py")
	if _, err := os.Stat(shim); err != nil {
		if sourceShim := filepath.Join("brainstem-go", "agent_shim.py"); fileExists(sourceShim) {
			shim = sourceShim
		} else {
			return nil, fmt.Errorf("locate agent shim: %w", err)
		}
	}

	python := firstNonempty(
		os.Getenv("BRAINSTEM_PYTHON"),
		os.Getenv("GRAIL_PYTHON"),
		"python3",
	)
	cfg := &config{
		port:         port,
		tokenURL:     strings.TrimSpace(os.Getenv("FAKE_TOKEN_URL")),
		modelURL:     strings.TrimSpace(os.Getenv("FAKE_MODEL_URL")),
		model:        firstNonempty(os.Getenv("GITHUB_MODEL"), "gpt-4o"),
		agentsPath:   strings.TrimSpace(os.Getenv("AGENTS_PATH")),
		python:       python,
		agentShim:    shim,
		agentsByName: make(map[string]agentDefinition),
	}
	if cfg.tokenURL == "" {
		return nil, errors.New("FAKE_TOKEN_URL is required")
	}
	if cfg.agentsPath == "" {
		return nil, errors.New("AGENTS_PATH is required")
	}

	agents, err := cfg.loadAgents()
	if err != nil {
		return nil, err
	}
	cfg.agents = agents
	for _, agent := range agents {
		cfg.agentsByName[agent.Name] = agent
	}
	return cfg, nil
}

func (cfg *config) loadAgents() ([]agentDefinition, error) {
	command := exec.Command(cfg.python, cfg.agentShim, "list", cfg.agentsPath)
	output, err := command.CombinedOutput()
	if err != nil {
		return nil, fmt.Errorf("load agents: %w: %s", err, strings.TrimSpace(string(output)))
	}
	var agents []agentDefinition
	if err := json.Unmarshal(output, &agents); err != nil {
		return nil, fmt.Errorf("decode agent list: %w", err)
	}
	sort.Slice(agents, func(i, j int) bool {
		return agents[i].Name < agents[j].Name
	})
	return agents, nil
}

func (cfg *config) handleHealth(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodGet {
		writeJSON(writer, http.StatusNotFound, map[string]any{"error": "Not found"})
		return
	}
	names := make([]string, 0, len(cfg.agents))
	for _, agent := range cfg.agents {
		names = append(names, agent.Name)
	}
	writeJSON(writer, http.StatusOK, map[string]any{
		"status": "ok",
		"agents": names,
	})
}

func (cfg *config) handleVersion(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodGet {
		writeJSON(writer, http.StatusNotFound, map[string]any{"error": "Not found"})
		return
	}
	writeJSON(writer, http.StatusOK, map[string]any{"version": kernelVersion})
}

func (cfg *config) handleChat(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		writeJSON(writer, http.StatusNotFound, map[string]any{"error": "Not found"})
		return
	}

	body, err := io.ReadAll(io.LimitReader(request.Body, 1<<20))
	if err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "Could not read request body."})
		return
	}
	var decoded any
	if err := decodeSingleJSON(body, &decoded); err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "Request body must be a JSON object"})
		return
	}
	input, ok := decoded.(map[string]any)
	if !ok {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "Request body must be a JSON object"})
		return
	}

	rawUserInput, exists := input["user_input"]
	if !exists {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "user_input is required"})
		return
	}
	userInput, ok := rawUserInput.(string)
	if !ok {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "user_input must be a string"})
		return
	}

	history, validationError := validateHistory(input["conversation_history"])
	if validationError != "" {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": validationError})
		return
	}

	userInput = strings.TrimSpace(userInput)
	if userInput == "" {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"error": "user_input is required"})
		return
	}

	sessionID, _ := input["session_id"].(string)
	requestedModel, _ := input["model"].(string)
	if strings.TrimSpace(requestedModel) == "" {
		requestedModel = cfg.model
	}

	response, actualModel, logs, err := cfg.complete(history, userInput, requestedModel)
	if err != nil {
		writeJSON(writer, http.StatusBadGateway, map[string]any{"error": err.Error()})
		return
	}
	writeJSON(writer, http.StatusOK, map[string]any{
		"response":        response,
		"session_id":      sessionID,
		"agent_logs":      logs,
		"voice_mode":      false,
		"model":           actualModel,
		"requested_model": requestedModel,
	})
}

func validateHistory(raw any) ([]map[string]any, string) {
	if raw == nil {
		return nil, ""
	}
	items, ok := raw.([]any)
	if !ok {
		return nil, "conversation_history must be an array"
	}
	history := make([]map[string]any, 0, len(items))
	for index, item := range items {
		turn, ok := item.(map[string]any)
		if !ok {
			return nil, fmt.Sprintf("conversation_history[%d] must be an object", index)
		}
		role, roleOK := turn["role"].(string)
		if !roleOK || (role != "user" && role != "assistant") {
			return nil, fmt.Sprintf("conversation_history[%d].role is invalid", index)
		}
		content, contentOK := turn["content"].(string)
		if !contentOK {
			return nil, fmt.Sprintf("conversation_history[%d].content must be a string", index)
		}
		history = append(history, map[string]any{
			"role":    role,
			"content": content,
		})
	}
	return history, ""
}

func (cfg *config) complete(
	history []map[string]any,
	userInput string,
	requestedModel string,
) (string, string, string, error) {
	messages := make([]map[string]any, 0, len(history)+8)
	messages = append(messages, history...)
	messages = append(messages, map[string]any{
		"role":    "user",
		"content": userInput,
	})

	tools := make([]map[string]any, 0, len(cfg.agents))
	for _, agent := range cfg.agents {
		tools = append(tools, map[string]any{
			"type":     "function",
			"function": agent.Metadata,
		})
	}

	logs := make([]string, 0)
	actualModel := requestedModel
	for round := 0; round < maxToolRounds; round++ {
		reply, model, err := cfg.callModel(messages, requestedModel, tools)
		if err != nil {
			return "", "", "", err
		}
		actualModel = model
		if len(reply.ToolCalls) == 0 {
			return normalizedResponse(reply.Content), actualModel, strings.Join(logs, "\n"), nil
		}

		messages = append(messages, assistantMessage(reply))
		for _, call := range reply.ToolCalls {
			result, logLine := cfg.executeTool(call)
			logs = append(logs, logLine)
			messages = append(messages, map[string]any{
				"role":         "tool",
				"tool_call_id": call.ID,
				"name":         call.Function.Name,
				"content":      result,
			})
		}
	}

	reply, model, err := cfg.callModel(messages, requestedModel, nil)
	if err != nil {
		return "", "", "", err
	}
	actualModel = model
	return normalizedResponse(reply.Content), actualModel, strings.Join(logs, "\n"), nil
}

func assistantMessage(message modelMessage) map[string]any {
	value := map[string]any{
		"role":       "assistant",
		"content":    nil,
		"tool_calls": message.ToolCalls,
	}
	if message.Content != nil {
		value["content"] = *message.Content
	}
	return value
}

func (cfg *config) callModel(
	messages []map[string]any,
	model string,
	tools []map[string]any,
) (modelMessage, string, error) {
	token, endpoint, err := cfg.getToken()
	if err != nil {
		return modelMessage{}, "", err
	}
	if endpoint == "" {
		endpoint = cfg.modelURL
	}
	if endpoint == "" {
		return modelMessage{}, "", errors.New("model endpoint is missing")
	}

	payload := map[string]any{
		"model":    model,
		"messages": messages,
	}
	if len(tools) > 0 {
		payload["tools"] = tools
	}
	body, err := json.Marshal(payload)
	if err != nil {
		return modelMessage{}, "", fmt.Errorf("encode model request: %w", err)
	}
	request, err := http.NewRequest(
		http.MethodPost,
		strings.TrimRight(endpoint, "/")+"/chat/completions",
		bytes.NewReader(body),
	)
	if err != nil {
		return modelMessage{}, "", fmt.Errorf("build model request: %w", err)
	}
	request.Header.Set("Authorization", "Bearer "+token)
	request.Header.Set("Content-Type", "application/json")

	response, err := http.DefaultClient.Do(request)
	if err != nil {
		return modelMessage{}, "", fmt.Errorf("call model: %w", err)
	}
	defer response.Body.Close()
	responseBody, err := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	if err != nil {
		return modelMessage{}, "", fmt.Errorf("read model response: %w", err)
	}
	if response.StatusCode != http.StatusOK {
		return modelMessage{}, "", fmt.Errorf(
			"model returned %s: %s",
			response.Status,
			strings.TrimSpace(string(responseBody)),
		)
	}

	var decoded modelResponse
	if err := json.Unmarshal(responseBody, &decoded); err != nil {
		return modelMessage{}, "", fmt.Errorf("decode model response: %w", err)
	}
	if len(decoded.Choices) == 0 {
		return modelMessage{}, "", errors.New("model response had no choices")
	}
	return decoded.Choices[0].Message, decoded.Model, nil
}

func (cfg *config) getToken() (string, string, error) {
	response, err := http.Get(cfg.tokenURL)
	if err != nil {
		return "", "", fmt.Errorf("get model token: %w", err)
	}
	defer response.Body.Close()
	body, err := io.ReadAll(io.LimitReader(response.Body, 1<<20))
	if err != nil {
		return "", "", fmt.Errorf("read model token: %w", err)
	}
	if response.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf(
			"token endpoint returned %s: %s",
			response.Status,
			strings.TrimSpace(string(body)),
		)
	}
	var token tokenResponse
	if err := json.Unmarshal(body, &token); err != nil {
		return "", "", fmt.Errorf("decode model token: %w", err)
	}
	if token.Token == "" {
		return "", "", errors.New("token endpoint returned an empty token")
	}
	return token.Token, token.Endpoints.API, nil
}

func (cfg *config) executeTool(call toolCall) (string, string) {
	logPrefix := "[" + call.Function.Name + "] "
	var arguments any
	if err := json.Unmarshal([]byte(call.Function.Arguments), &arguments); err != nil {
		message := "Error: Tool arguments must be a valid JSON object."
		return message, logPrefix + message
	}
	object, ok := arguments.(map[string]any)
	if !ok {
		message := "Error: Tool arguments must be a valid JSON object."
		return message, logPrefix + message
	}
	if _, exists := cfg.agentsByName[call.Function.Name]; !exists {
		message := fmt.Sprintf("Agent '%s' not found.", call.Function.Name)
		return message, message
	}
	encoded, err := json.Marshal(object)
	if err != nil {
		message := "Error: " + err.Error()
		return message, logPrefix + "ERROR: " + err.Error()
	}
	command := exec.Command(
		cfg.python,
		cfg.agentShim,
		"call",
		cfg.agentsPath,
		call.Function.Name,
		string(encoded),
	)
	output, err := command.CombinedOutput()
	if err != nil {
		detail := strings.TrimSpace(string(output))
		message := "Error: " + detail
		return message, logPrefix + "ERROR: " + detail
	}
	var result shimResult
	if err := json.Unmarshal(output, &result); err != nil {
		message := "Error: " + err.Error()
		return message, logPrefix + "ERROR: " + err.Error()
	}
	if !result.OK {
		return "Error: " + result.Error, logPrefix + "ERROR: " + result.Error
	}
	return result.Result, logPrefix + result.Result
}

func normalizedResponse(content *string) string {
	if content == nil || strings.TrimSpace(*content) == "" {
		return emptyResponsePrompt
	}
	return *content
}

func decodeSingleJSON(body []byte, target any) error {
	decoder := json.NewDecoder(bytes.NewReader(body))
	decoder.UseNumber()
	if err := decoder.Decode(target); err != nil {
		return err
	}
	var trailing any
	if err := decoder.Decode(&trailing); err != io.EOF {
		if err == nil {
			return errors.New("multiple JSON values")
		}
		return err
	}
	return nil
}

func writeJSON(writer http.ResponseWriter, status int, value any) {
	body, err := json.Marshal(value)
	if err != nil {
		http.Error(writer, `{"error":"Could not encode response."}`, http.StatusInternalServerError)
		return
	}
	writer.Header().Set("Content-Type", "application/json")
	writer.WriteHeader(status)
	_, _ = writer.Write(body)
}

func firstNonempty(values ...string) string {
	for _, value := range values {
		if strings.TrimSpace(value) != "" {
			return strings.TrimSpace(value)
		}
	}
	return ""
}

func fileExists(path string) bool {
	_, err := os.Stat(path)
	return err == nil
}
