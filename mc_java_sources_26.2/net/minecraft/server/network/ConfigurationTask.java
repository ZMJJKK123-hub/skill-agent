package net.minecraft.server.network;

import java.util.function.Consumer;
import net.minecraft.network.protocol.Packet;
import net.minecraftforge.network.config.ConfigurationTaskContext;

public interface ConfigurationTask {
   default void start(ConfigurationTaskContext ctx) {
      this.start(ctx::send);
   }

   void start(Consumer<Packet<?>> var1);

   default boolean tick() {
      return false;
   }

   ConfigurationTask.Type type();

   record Type(String id) {
      @Override
      public String toString() {
         return this.id;
      }
   }
}
