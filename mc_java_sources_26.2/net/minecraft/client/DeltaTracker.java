package net.minecraft.client;

import it.unimi.dsi.fastutil.floats.FloatUnaryOperator;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import net.minecraftforge.client.ForgeHooksClient;

@OnlyIn(Dist.CLIENT)
public interface DeltaTracker {
   DeltaTracker ZERO = new DeltaTracker.DefaultValue(0.0F);
   DeltaTracker ONE = new DeltaTracker.DefaultValue(1.0F);

   float getGameTimeDeltaTicks();

   float getGameTimeDeltaPartialTick(boolean var1);

   float getRealtimeDeltaTicks();

   @OnlyIn(Dist.CLIENT)
   class DefaultValue implements DeltaTracker {
      private final float value;

      private DefaultValue(float value) {
         this.value = value;
      }

      @Override
      public float getGameTimeDeltaTicks() {
         return this.value;
      }

      @Override
      public float getGameTimeDeltaPartialTick(boolean ignored) {
         return this.value;
      }

      @Override
      public float getRealtimeDeltaTicks() {
         return this.value;
      }
   }

   @OnlyIn(Dist.CLIENT)
   class Timer implements DeltaTracker {
      private float deltaTicks;
      private float deltaTickResidual;
      private float realtimeDeltaTicks;
      private float pausedDeltaTickResidual;
      private long lastMs;
      private long lastUiMs;
      private final float msPerTick;
      private final FloatUnaryOperator targetMsptProvider;
      private boolean paused;
      private boolean frozen;

      public Timer(float ticksPerSecond, long currentMs, FloatUnaryOperator targetMsptProvider) {
         this.msPerTick = 1000.0F / ticksPerSecond;
         this.lastUiMs = this.lastMs = currentMs;
         this.targetMsptProvider = targetMsptProvider;
      }

      public int advanceGameTime(long currentMs) {
         this.deltaTicks = (float)(currentMs - this.lastMs) / this.targetMsptProvider.apply(this.msPerTick);
         this.lastMs = currentMs;
         this.deltaTickResidual = this.deltaTickResidual + this.deltaTicks;
         int ticks = (int)this.deltaTickResidual;
         this.deltaTickResidual -= ticks;
         return ticks;
      }

      public void advanceRealTime(long currentMs) {
         this.realtimeDeltaTicks = (float)(currentMs - this.lastUiMs) / this.msPerTick;
         this.lastUiMs = currentMs;
      }

      public void updatePauseState(boolean pauseState) {
         if (pauseState) {
            this.pause();
         } else {
            this.unPause();
         }
      }

      private void pause() {
         if (!this.paused) {
            if (ForgeHooksClient.onClientPauseChangePre(true)) {
               return;
            }

            this.pausedDeltaTickResidual = this.deltaTickResidual;
         }

         this.paused = true;
         ForgeHooksClient.onClientPauseChangePost(true);
      }

      private void unPause() {
         if (this.paused) {
            if (ForgeHooksClient.onClientPauseChangePre(false)) {
               return;
            }

            this.deltaTickResidual = this.pausedDeltaTickResidual;
         }

         this.paused = false;
         ForgeHooksClient.onClientPauseChangePost(false);
      }

      public void updateFrozenState(boolean frozen) {
         this.frozen = frozen;
      }

      @Override
      public float getGameTimeDeltaTicks() {
         return this.deltaTicks;
      }

      @Override
      public float getGameTimeDeltaPartialTick(boolean ignoreFrozenGame) {
         if (!ignoreFrozenGame && this.frozen) {
            return 1.0F;
         } else {
            return this.paused ? this.pausedDeltaTickResidual : this.deltaTickResidual;
         }
      }

      @Override
      public float getRealtimeDeltaTicks() {
         return this.realtimeDeltaTicks > 7.0F ? 0.5F : this.realtimeDeltaTicks;
      }
   }
}
