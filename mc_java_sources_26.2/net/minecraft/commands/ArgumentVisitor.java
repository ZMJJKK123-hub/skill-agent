package net.minecraft.commands;

import com.mojang.brigadier.ParseResults;
import com.mojang.brigadier.context.CommandContextBuilder;
import com.mojang.brigadier.context.ParsedArgument;
import com.mojang.brigadier.context.ParsedCommandNode;
import com.mojang.brigadier.tree.ArgumentCommandNode;
import java.util.Map;
import org.jspecify.annotations.Nullable;

public class ArgumentVisitor {
   public static <S> void visitArguments(ParseResults<S> command, ArgumentVisitor.Output<S> output, boolean rejectRootRedirects) {
      CommandContextBuilder<S> rootContext = command.getContext();
      CommandContextBuilder<S> context = rootContext;
      visitNodeArguments(context, output);

      CommandContextBuilder<S> child;
      while ((child = context.getChild()) != null && (!rejectRootRedirects || child.getRootNode() != rootContext.getRootNode())) {
         visitNodeArguments(child, output);
         context = child;
      }
   }

   private static <S> void visitNodeArguments(CommandContextBuilder<S> context, ArgumentVisitor.Output<S> output) {
      Map<String, ParsedArgument<S, ?>> values = context.getArguments();

      for (ParsedCommandNode<S> node : context.getNodes()) {
         if (node.getNode() instanceof ArgumentCommandNode<S, ?> argument) {
            ParsedArgument<S, ?> value = values.get(argument.getName());
            callVisitor(context, output, argument, value);
         }
      }
   }

   private static <S, T> void callVisitor(
      CommandContextBuilder<S> context, ArgumentVisitor.Output<S> output, ArgumentCommandNode<S, T> argument, @Nullable ParsedArgument<S, ?> value
   ) {
      output.accept(context, argument, (ParsedArgument<S, T>)value);
   }

   @FunctionalInterface
   public interface Output<S> {
      <T> void accept(CommandContextBuilder<S> var1, ArgumentCommandNode<S, T> var2, @Nullable ParsedArgument<S, T> var3);
   }
}
