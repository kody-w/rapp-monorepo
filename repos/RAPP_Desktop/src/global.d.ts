import type { RappDesktopApi } from './desktop-api'

declare global {
  interface Window {
    rappDesktop: RappDesktopApi
  }
}

export {}
