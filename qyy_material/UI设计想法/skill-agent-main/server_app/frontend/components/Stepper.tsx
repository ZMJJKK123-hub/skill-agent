interface StepperProps {
  current: 1 | 2 | 3;
}

export default function Stepper({ current }: StepperProps) {
  const steps = [1, 2, 3] as const;
  return (
    <div className="mb-8 flex items-center justify-center gap-2">
      {steps.map((n) => {
        const done = n < current;
        const active = n === current;
        return (
          <div key={n} className="flex items-center gap-2">
            {n > 1 && (
              <div
                className={`h-px w-10 transition-colors duration-300 ${
                  done ? "bg-forge-emerald/60" : "bg-white/10"
                }`}
              />
            )}
            <div
              className={`h-3 w-3 rounded-full transition-all duration-300 ${
                active
                  ? "scale-125 bg-gradient-to-r from-forge-cyan to-forge-emerald shadow-glow"
                  : done
                    ? "bg-forge-emerald/70"
                    : "bg-white/15"
              }`}
            />
          </div>
        );
      })}
    </div>
  );
}