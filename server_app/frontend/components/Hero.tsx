export default function Hero() {
  return (
    <section className="relative px-5 pt-14 pb-8 text-center">
      <div className="flex flex-col items-center justify-center text-center space-y-4">
        <h1 className="font-semibold tracking-tight">
          <span className="bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-3xl text-transparent md:text-4xl">
            AI 驱动的
          </span>
          <span className="mx-1.5 bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-3xl font-bold text-transparent md:text-4xl">
            MOD
          </span>
          <span className="bg-gradient-to-b from-white to-zinc-400 bg-clip-text text-3xl text-transparent md:text-4xl">
            制作器
          </span>
        </h1>
        <p className="text-sm text-zinc-400 tracking-wider">
          输入你的想法，剩下的交由智能体完成。
        </p>
      </div>
    </section>
  );
}