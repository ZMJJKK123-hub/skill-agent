package net.minecraft.commands.execution;

import com.mojang.brigadier.Command;
import com.mojang.brigadier.context.CommandContext;
import com.mojang.brigadier.context.ContextChain;
import com.mojang.brigadier.exceptions.CommandSyntaxException;
import net.minecraft.commands.ExecutionCommandSource;
import org.jspecify.annotations.Nullable;

public interface CustomCommandExecutor<T> {
   void run(T var1, ContextChain<T> var2, ChainModifiers var3, ExecutionControl<T> var4);

   interface CommandAdapter<T> extends CustomCommandExecutor<T>, Command<T> {
      default int run(CommandContext<T> context) throws CommandSyntaxException {
         throw new UnsupportedOperationException("This function should not run");
      }
   }

   abstract class WithErrorHandling<T extends ExecutionCommandSource<T>> implements CustomCommandExecutor<T> {
      public final void run(T sender, ContextChain<T> currentStep, ChainModifiers modifiers, ExecutionControl<T> output) {
         try {
            this.runGuarded(sender, currentStep, modifiers, output);
         } catch (CommandSyntaxException e) {
            this.onError(e, sender, modifiers, output.tracer());
            sender.callback().onFailure();
         }
      }

      protected void onError(CommandSyntaxException e, T sender, ChainModifiers modifiers, @Nullable TraceCallbacks tracer) {
         sender.handleError(e, modifiers.isForked(), tracer);
      }

      protected abstract void runGuarded(T var1, ContextChain<T> var2, ChainModifiers var3, ExecutionControl<T> var4) throws CommandSyntaxException;
   }
}
