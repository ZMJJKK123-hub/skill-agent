/**
 * agent 提问卡片：多题作答（选项点选 + 自由填写），一次性提交。
 * 由 conversation.tsx 原样迁出，行为不变。
 */
import { useState } from 'react'
import { useT } from '../../../lib/i18n'
import { useSession } from '../../../lib/session'
import { answerQuestion } from '../../../lib/session'

export function QuestionCard() {
  const sess = useSession()
  const t = useT()
  // 支持多题：questions（数组）优先；兼容单题 question
  const qs = sess.questions ?? (sess.question ? [sess.question] : null)
  // 每题的草稿答案（index → string）；null = 未作答
  const [drafts, setDrafts] = useState<Record<number, string>>({})
  const [customText, setCustomText] = useState<Record<number, string>>({})

  if (!qs || qs.length === 0) return null

  // 点选项：暂存为该题答案（不提交！可随时改）
  const pick = (idx: number, opt: string) => {
    setDrafts((d) => ({ ...d, [idx]: opt }))
    setCustomText((c) => ({ ...c, [idx]: '' }))
  }
  // 自由填写：输入即暂存（不提交）
  const type = (idx: number, v: string) => {
    setCustomText((c) => ({ ...c, [idx]: v }))
    if (v.trim()) setDrafts((d) => ({ ...d, [idx]: v.trim() }))
  }
  // 确认：一次性提交所有题目的答案
  const confirmAll = () => {
    const answers = qs.map((q, i) => ({
      question: q.question,
      answer: drafts[i] ?? customText[i]?.trim() ?? '',
    }))
    answerQuestion('', answers)
    setDrafts({})
    setCustomText({})
  }
  const answeredCount = qs.filter((_, i) => (drafts[i] ?? '').trim()).length
  const allAnswered = answeredCount === qs.length

  return (
    <div className="mb-2 rounded-xl border border-forge-500/40 bg-forge-500/10 p-3">
      <div className="mb-1 text-xs text-faint">
        {t('conv.questionTitle')}（{answeredCount}/{qs.length}）
      </div>
      <div className="space-y-3">
        {qs.map((q, i) => (
          <div key={i} className="rounded-lg border border-line bg-panel/50 p-2">
            <div className="mb-1.5 text-sm font-medium text-forge-300">
              {i + 1}. {q.question}
            </div>
            {q.options.length > 0 && (
              <div className="mb-1.5 flex flex-wrap gap-1.5">
                {q.options.map((o) => (
                  <button
                    key={o}
                    onClick={() => pick(i, o)}
                    className={`rounded-md border px-2.5 py-1 text-xs transition ${
                      drafts[i] === o
                        ? 'border-forge-500 bg-forge-500/20 text-forge-300'
                        : 'border-forge-500/30 text-forge-400 hover:bg-forge-500/10'
                    }`}
                  >
                    {o}
                  </button>
                ))}
              </div>
            )}
            <input
              value={customText[i] ?? ''}
              onChange={(e) => type(i, e.target.value)}
              placeholder={drafts[i] && drafts[i] !== customText[i] ? `已选「${drafts[i]}」，可在此修改或自填…` : '也可自行填写…'}
              className="w-full rounded-md border border-line bg-field px-2 py-1 text-xs outline-none placeholder:text-faint focus:border-forge-500"
            />
            {drafts[i] && (
              <div className="mt-1 text-[11px] text-faint">
                当前答案：{drafts[i]}
                <button
                  onClick={() => {
                    setDrafts((d) => { const n = { ...d }; delete n[i]; return n })
                    setCustomText((c) => { const n = { ...c }; delete n[i]; return n })
                  }}
                  className="ml-2 text-red-400 hoverable"
                >
                  ✕ 清除
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="mt-2 flex items-center gap-2">
        <button
          onClick={confirmAll}
          disabled={!allAnswered}
          className="rounded-md bg-forge-500 px-4 py-1.5 text-sm font-medium text-ink-950 hover:bg-forge-400 disabled:opacity-40"
        >
          {t('conv.questionConfirm')} {allAnswered ? '' : `（还差 ${qs.length - answeredCount} 题）`}
        </button>
        {!allAnswered && <span className="text-xs text-faint">全部回答后即可确认，可随时修改</span>}
      </div>
    </div>
  )
}
