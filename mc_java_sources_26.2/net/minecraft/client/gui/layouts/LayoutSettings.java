package net.minecraft.client.gui.layouts;

import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;

@OnlyIn(Dist.CLIENT)
public interface LayoutSettings {
   LayoutSettings padding(int var1);

   LayoutSettings padding(int var1, int var2);

   LayoutSettings padding(int var1, int var2, int var3, int var4);

   LayoutSettings paddingLeft(int var1);

   LayoutSettings paddingTop(int var1);

   LayoutSettings paddingRight(int var1);

   LayoutSettings paddingBottom(int var1);

   LayoutSettings paddingHorizontal(int var1);

   LayoutSettings paddingVertical(int var1);

   LayoutSettings align(float var1, float var2);

   LayoutSettings alignHorizontally(float var1);

   LayoutSettings alignVertically(float var1);

   default LayoutSettings alignHorizontallyLeft() {
      return this.alignHorizontally(0.0F);
   }

   default LayoutSettings alignHorizontallyCenter() {
      return this.alignHorizontally(0.5F);
   }

   default LayoutSettings alignHorizontallyRight() {
      return this.alignHorizontally(1.0F);
   }

   default LayoutSettings alignVerticallyTop() {
      return this.alignVertically(0.0F);
   }

   default LayoutSettings alignVerticallyMiddle() {
      return this.alignVertically(0.5F);
   }

   default LayoutSettings alignVerticallyBottom() {
      return this.alignVertically(1.0F);
   }

   LayoutSettings copy();

   LayoutSettings.LayoutSettingsImpl getExposed();

   static LayoutSettings defaults() {
      return new LayoutSettings.LayoutSettingsImpl();
   }

   @OnlyIn(Dist.CLIENT)
   class LayoutSettingsImpl implements LayoutSettings {
      public int paddingLeft;
      public int paddingTop;
      public int paddingRight;
      public int paddingBottom;
      public float xAlignment;
      public float yAlignment;

      public LayoutSettingsImpl() {
      }

      public LayoutSettingsImpl(LayoutSettings.LayoutSettingsImpl copy) {
         this.paddingLeft = copy.paddingLeft;
         this.paddingTop = copy.paddingTop;
         this.paddingRight = copy.paddingRight;
         this.paddingBottom = copy.paddingBottom;
         this.xAlignment = copy.xAlignment;
         this.yAlignment = copy.yAlignment;
      }

      public LayoutSettings.LayoutSettingsImpl padding(int padding) {
         return this.padding(padding, padding);
      }

      public LayoutSettings.LayoutSettingsImpl padding(int horizontal, int vertical) {
         return this.paddingHorizontal(horizontal).paddingVertical(vertical);
      }

      public LayoutSettings.LayoutSettingsImpl padding(int left, int top, int right, int bottom) {
         return this.paddingLeft(left).paddingRight(right).paddingTop(top).paddingBottom(bottom);
      }

      public LayoutSettings.LayoutSettingsImpl paddingLeft(int padding) {
         this.paddingLeft = padding;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl paddingTop(int padding) {
         this.paddingTop = padding;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl paddingRight(int padding) {
         this.paddingRight = padding;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl paddingBottom(int padding) {
         this.paddingBottom = padding;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl paddingHorizontal(int padding) {
         return this.paddingLeft(padding).paddingRight(padding);
      }

      public LayoutSettings.LayoutSettingsImpl paddingVertical(int padding) {
         return this.paddingTop(padding).paddingBottom(padding);
      }

      public LayoutSettings.LayoutSettingsImpl align(float xAlignment, float yAlignment) {
         this.xAlignment = xAlignment;
         this.yAlignment = yAlignment;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl alignHorizontally(float xAlignment) {
         this.xAlignment = xAlignment;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl alignVertically(float yAlignment) {
         this.yAlignment = yAlignment;
         return this;
      }

      public LayoutSettings.LayoutSettingsImpl copy() {
         return new LayoutSettings.LayoutSettingsImpl(this);
      }

      @Override
      public LayoutSettings.LayoutSettingsImpl getExposed() {
         return this;
      }
   }
}
