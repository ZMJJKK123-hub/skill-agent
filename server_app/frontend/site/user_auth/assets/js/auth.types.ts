export interface User { username: string }
export interface AuthResult extends User { token: string }
export interface TokenStore { get(): string | null; set(token: string): void; clear(): void }
export interface AuthRepository {
  login(username: string, password: string): Promise<AuthResult>
  register(username: string, password: string): Promise<AuthResult>
  me(): Promise<User>
  logout(): Promise<void>
}
export interface AuthController {
  restore(): Promise<void>
  login(username: string, password: string): Promise<void>
  register(username: string, password: string): Promise<void>
  logout(): Promise<void>
}
