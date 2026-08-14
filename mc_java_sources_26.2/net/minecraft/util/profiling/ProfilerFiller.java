package net.minecraft.util.profiling;

import java.util.function.Supplier;
import net.minecraft.util.profiling.metrics.MetricCategory;

public interface ProfilerFiller {
   String ROOT = "root";

   void startTick();

   void endTick();

   void push(String var1);

   void push(Supplier<String> var1);

   void pop();

   void popPush(String var1);

   void popPush(Supplier<String> var1);

   default void addZoneText(String text) {
   }

   default void addZoneValue(long value) {
   }

   default void setZoneColor(int color) {
   }

   default Zone zone(String name) {
      this.push(name);
      return new Zone(this);
   }

   default Zone zone(Supplier<String> name) {
      this.push(name);
      return new Zone(this);
   }

   void markForCharting(MetricCategory var1);

   default void incrementCounter(String name) {
      this.incrementCounter(name, 1);
   }

   void incrementCounter(String var1, int var2);

   default void incrementCounter(Supplier<String> name) {
      this.incrementCounter(name, 1);
   }

   void incrementCounter(Supplier<String> var1, int var2);

   static ProfilerFiller combine(ProfilerFiller first, ProfilerFiller second) {
      if (first == InactiveProfiler.INSTANCE) {
         return second;
      } else {
         return second == InactiveProfiler.INSTANCE ? first : new ProfilerFiller.CombinedProfileFiller(first, second);
      }
   }

   class CombinedProfileFiller implements ProfilerFiller {
      private final ProfilerFiller first;
      private final ProfilerFiller second;

      public CombinedProfileFiller(ProfilerFiller first, ProfilerFiller second) {
         this.first = first;
         this.second = second;
      }

      @Override
      public void startTick() {
         this.first.startTick();
         this.second.startTick();
      }

      @Override
      public void endTick() {
         this.first.endTick();
         this.second.endTick();
      }

      @Override
      public void push(String name) {
         this.first.push(name);
         this.second.push(name);
      }

      @Override
      public void push(Supplier<String> name) {
         this.first.push(name);
         this.second.push(name);
      }

      @Override
      public void markForCharting(MetricCategory category) {
         this.first.markForCharting(category);
         this.second.markForCharting(category);
      }

      @Override
      public void pop() {
         this.first.pop();
         this.second.pop();
      }

      @Override
      public void popPush(String name) {
         this.first.popPush(name);
         this.second.popPush(name);
      }

      @Override
      public void popPush(Supplier<String> name) {
         this.first.popPush(name);
         this.second.popPush(name);
      }

      @Override
      public void incrementCounter(String name, int amount) {
         this.first.incrementCounter(name, amount);
         this.second.incrementCounter(name, amount);
      }

      @Override
      public void incrementCounter(Supplier<String> name, int amount) {
         this.first.incrementCounter(name, amount);
         this.second.incrementCounter(name, amount);
      }

      @Override
      public void addZoneText(String text) {
         this.first.addZoneText(text);
         this.second.addZoneText(text);
      }

      @Override
      public void addZoneValue(long value) {
         this.first.addZoneValue(value);
         this.second.addZoneValue(value);
      }

      @Override
      public void setZoneColor(int color) {
         this.first.setZoneColor(color);
         this.second.setZoneColor(color);
      }
   }
}
