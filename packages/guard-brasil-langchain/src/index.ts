/**
 * @egosbr/guard-brasil-langchain
 * Guard Brasil middleware for LangChain — Brazilian PII protection
 *
 * Usage:
 *   import { createGuardMiddleware, GuardBrasilRunnable } from '@egosbr/guard-brasil-langchain'
 */

import { GuardBrasil } from '@egosbr/guard-brasil'
import type { GuardBrasilConfig } from '@egosbr/guard-brasil'

export interface GuardMiddlewareOptions {
  /** Guard Brasil API key (for remote API mode) */
  apiKey?: string
  /** Guard Brasil config options */
  config?: GuardBrasilConfig
  /** If true, throws when PII found. Default: false (mask and continue) */
  throwOnPII?: boolean
  /** Callback when PII is detected */
  onPIIDetected?: (categories: string[], text: string) => void
}

/**
 * Creates a Guard Brasil redact function compatible with LangChain's piiMiddleware.
 *
 * @example
 * import { piiMiddleware } from 'langchain'
 * import { createGuardRedact } from '@egosbr/guard-brasil-langchain'
 *
 * const chain = new LLMChain({
 *   middlewares: [piiMiddleware({ redact: createGuardRedact() })]
 * })
 */
export function createGuardRedact(options: GuardMiddlewareOptions = {}) {
  const guard = GuardBrasil.create(options.config)

  return (text: string): string => {
    const result = guard.inspect(text)

    if (result.masking.findings.length > 0 && options.onPIIDetected) {
      const categories = result.masking.findings.map(f => f.category)
      options.onPIIDetected(categories, text)
    }

    if (result.masking.findings.length > 0 && options.throwOnPII) {
      throw new Error(`PII detectado: ${result.masking.findings.map(f => f.label).join(', ')}`)
    }

    return result.output
  }
}

/**
 * LangChain Runnable that wraps Guard Brasil inspection.
 * Can be piped before any LLM call.
 *
 * @example
 * import { GuardBrasilRunnable } from '@egosbr/guard-brasil-langchain'
 * import { ChatOpenAI } from '@langchain/openai'
 *
 * const chain = new GuardBrasilRunnable()
 *   .pipe(new ChatOpenAI({ modelName: 'gpt-4o' }))
 *
 * const result = await chain.invoke("O CPF do cliente é 123.456.789-09")
 * // CPF is masked before reaching OpenAI
 */
export class GuardBrasilRunnable {
  private guard: GuardBrasil
  private options: GuardMiddlewareOptions

  constructor(options: GuardMiddlewareOptions = {}) {
    this.guard = GuardBrasil.create(options.config)
    this.options = options
  }

  async invoke(input: string): Promise<string> {
    const result = this.guard.inspect(input)

    if (result.masking.findings.length > 0 && this.options.onPIIDetected) {
      this.options.onPIIDetected(
        result.masking.findings.map(f => f.category),
        input
      )
    }

    return result.output
  }

  pipe(next: { invoke: (input: string) => Promise<unknown> }) {
    return {
      invoke: async (input: string) => {
        const masked = await this.invoke(input)
        return next.invoke(masked)
      }
    }
  }
}

/**
 * Guard Brasil middleware for OpenAI SDK — wraps createCompletion.
 *
 * @example
 * import OpenAI from 'openai'
 * import { guardOpenAI } from '@egosbr/guard-brasil-langchain'
 *
 * const openai = guardOpenAI(new OpenAI({ apiKey: process.env.OPENAI_API_KEY }))
 *
 * // CPFs in messages are automatically masked before reaching OpenAI
 * const response = await openai.chat.completions.create({
 *   model: 'gpt-4o',
 *   messages: [{ role: 'user', content: 'O CPF 123.456.789-09 do cliente...' }]
 * })
 */
export function guardOpenAI(client: object, options: GuardMiddlewareOptions = {}) {
  const guard = GuardBrasil.create(options.config)

  return new Proxy(client, {
    get(target: Record<string, unknown>, prop: string) {
      if (prop === 'chat') {
        return new Proxy(target.chat as Record<string, unknown>, {
          get(chatTarget: Record<string, unknown>, chatProp: string) {
            if (chatProp === 'completions') {
              return new Proxy(chatTarget.completions as Record<string, unknown>, {
                get(compTarget: Record<string, unknown>, compProp: string) {
                  if (compProp === 'create') {
                    return (params: { messages?: Array<{ role: string; content: unknown }> }) => {
                      const maskedParams = {
                        ...params,
                        messages: params.messages?.map((msg) => ({
                          ...msg,
                          content: typeof msg.content === 'string'
                            ? guard.inspect(msg.content).output
                            : msg.content
                        }))
                      }
                      return (compTarget.create as (p: typeof maskedParams) => unknown)(maskedParams)
                    }
                  }
                  return compTarget[compProp]
                }
              })
            }
            return chatTarget[chatProp]
          }
        })
      }
      return (target as Record<string, unknown>)[prop]
    }
  })
}

/**
 * Guard Brasil middleware for Anthropic SDK.
 *
 * @example
 * import Anthropic from '@anthropic-ai/sdk'
 * import { guardAnthropic } from '@egosbr/guard-brasil-langchain'
 *
 * const claude = guardAnthropic(new Anthropic())
 * const msg = await claude.messages.create({
 *   model: 'claude-opus-4-6',
 *   messages: [{ role: 'user', content: 'CPF 123.456.789-09...' }]
 * })
 */
export function guardAnthropic(client: object, options: GuardMiddlewareOptions = {}) {
  const guard = GuardBrasil.create(options.config)

  return new Proxy(client, {
    get(target: Record<string, unknown>, prop: string) {
      if (prop === 'messages') {
        return new Proxy(target.messages as Record<string, unknown>, {
          get(msgTarget: Record<string, unknown>, msgProp: string) {
            if (msgProp === 'create') {
              return (params: { messages?: Array<{ role: string; content: unknown }> }) => {
                const maskedParams = {
                  ...params,
                  messages: params.messages?.map((msg) => ({
                    ...msg,
                    content: typeof msg.content === 'string'
                      ? guard.inspect(msg.content).output
                      : msg.content
                  }))
                }
                return (msgTarget.create as (p: typeof maskedParams) => unknown)(maskedParams)
              }
            }
            return msgTarget[msgProp]
          }
        })
      }
      return (target as Record<string, unknown>)[prop]
    }
  })
}

export { GuardBrasil }
export type { GuardBrasilConfig }
