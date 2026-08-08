package net.minecraft.client.gui.screens.inventory.tooltip;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.inventory.tooltip.BundleTooltip;
import net.minecraft.world.inventory.tooltip.TooltipComponent;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.gui.ClientTooltipComponentManager;

@OnlyIn(Dist.CLIENT)
public interface ClientTooltipComponent {
   static ClientTooltipComponent create(FormattedCharSequence charSequence) {
      return new ClientTextTooltip(charSequence);
   }

   static ClientTooltipComponent create(TooltipComponent component) {
      return switch (component) {
         case BundleTooltip bundleTooltip -> new ClientBundleTooltip(bundleTooltip.contents());
         case ClientActivePlayersTooltip.ActivePlayersTooltip activePlayersTooltip -> new ClientActivePlayersTooltip(activePlayersTooltip);
         default -> ClientTooltipComponentManager.createClientTooltipComponent(component);
      };
   }

   int getHeight(Font var1);

   int getWidth(Font var1);

   default boolean showTooltipWithItemInHand() {
      return false;
   }

   default void extractText(GuiGraphicsExtractor graphics, Font font, int x, int y) {
   }

   default void extractImage(Font font, int x, int y, int w, int h, GuiGraphicsExtractor graphics) {
   }
}
