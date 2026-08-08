package net.minecraft.network.protocol.login.custom;

import java.util.function.Consumer;
import net.minecraft.network.FriendlyByteBuf;
import net.minecraft.resources.Identifier;
import org.jetbrains.annotations.Nullable;

public record DiscardedQueryPayload(Identifier id, @Nullable FriendlyByteBuf data, Consumer<FriendlyByteBuf> encoder) implements CustomQueryPayload {
   public DiscardedQueryPayload(Identifier id) {
      this(id, null, buf -> {});
   }

   @Override
   public void write(FriendlyByteBuf output) {
      if (this.data != null) {
         output.writeBytes(this.data.slice());
      } else {
         this.encoder.accept(output);
      }
   }
}
