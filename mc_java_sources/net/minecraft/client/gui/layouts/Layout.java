package net.minecraft.client.gui.layouts;

import java.util.function.Consumer;
import net.minecraft.client.gui.components.AbstractWidget;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface Layout extends LayoutElement {
   void visitChildren(Consumer<LayoutElement> var1);

   @Override
   default void visitWidgets(Consumer<AbstractWidget> widgetVisitor) {
      this.visitChildren(child -> child.visitWidgets(widgetVisitor));
   }

   default void arrangeElements() {
      this.visitChildren(child -> {
         if (child instanceof Layout layout) {
            layout.arrangeElements();
         }
      });
   }

   void removeChildren();
}
