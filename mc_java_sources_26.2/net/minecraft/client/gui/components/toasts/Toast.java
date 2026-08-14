package net.minecraft.client.gui.components.toasts;

import net.minecraft.client.gui.Font;
import net.minecraft.client.gui.GuiGraphicsExtractor;
import net.minecraft.client.resources.sounds.SimpleSoundInstance;
import net.minecraft.client.sounds.SoundManager;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.util.Mth;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface Toast {
   Object NO_TOKEN = new Object();
   int DEFAULT_WIDTH = 160;
   int SLOT_HEIGHT = 32;

   Toast.Visibility getWantedVisibility();

   void update(ToastManager var1, long var2);

   default @Nullable SoundEvent getSoundEvent() {
      return null;
   }

   void extractRenderState(GuiGraphicsExtractor var1, Font var2, long var3);

   default Object getToken() {
      return NO_TOKEN;
   }

   default float xPos(int screenWidth, float visiblePortion) {
      return screenWidth - this.width() * visiblePortion;
   }

   default float yPos(int firstSlotIndex) {
      return firstSlotIndex * this.height();
   }

   default int width() {
      return 160;
   }

   default int height() {
      return 32;
   }

   default int occcupiedSlotCount() {
      return Mth.positiveCeilDiv(this.height(), 32);
   }

   default void onFinishedRendering() {
   }

   @OnlyIn(Dist.CLIENT)
   enum Visibility {
      SHOW(SoundEvents.UI_TOAST_IN),
      HIDE(SoundEvents.UI_TOAST_OUT);

      private final SoundEvent soundEvent;

      Visibility(final SoundEvent soundEvent) {
         this.soundEvent = soundEvent;
      }

      public void playSound(SoundManager manager) {
         manager.play(SimpleSoundInstance.forUI(this.soundEvent, 1.0F, 1.0F));
      }
   }
}
