package net.minecraft.network;

import io.netty.buffer.ByteBuf;
import io.netty.channel.ChannelHandlerContext;
import io.netty.handler.codec.MessageToByteEncoder;
import java.util.zip.Deflater;
import net.minecraftforge.common.util.HexDumper;
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class CompressionEncoder extends MessageToByteEncoder<ByteBuf> {
   private static final boolean DISABLE_PACKET_DEBUG = Boolean.parseBoolean(System.getProperty("forge.disablePacketCompressionDebug", "false"));
   private static final Logger LOGGER = LogManager.getLogger();
   private final byte[] encodeBuf = new byte[8192];
   private final Deflater deflater;
   private int threshold;

   public CompressionEncoder(int threshold) {
      this.threshold = threshold;
      this.deflater = new Deflater();
   }

   protected void encode(ChannelHandlerContext ctx, ByteBuf uncompressed, ByteBuf out) {
      int uncompressedLength = uncompressed.readableBytes();
      if (uncompressedLength > 8388608) {
         throw new IllegalArgumentException("Packet too big (is " + uncompressedLength + ", should be less than 8388608)");
      }

      if (uncompressedLength < this.threshold) {
         VarInt.write(out, 0);
         out.writeBytes(uncompressed);
      } else {
         if (!DISABLE_PACKET_DEBUG && uncompressedLength > 8388608) {
            uncompressed.markReaderIndex();
            LOGGER.error("Attempted to send packet over maximum protocol size: {} > {}\nData:\n{}", uncompressedLength, 8388608, HexDumper.dump(uncompressed));
            uncompressed.resetReaderIndex();
         }

         byte[] input = new byte[uncompressedLength];
         uncompressed.readBytes(input);
         VarInt.write(out, input.length);
         this.deflater.setInput(input, 0, uncompressedLength);
         this.deflater.finish();

         while (!this.deflater.finished()) {
            int written = this.deflater.deflate(this.encodeBuf);
            out.writeBytes(this.encodeBuf, 0, written);
         }

         this.deflater.reset();
      }
   }

   public int getThreshold() {
      return this.threshold;
   }

   public void setThreshold(int threshold) {
      this.threshold = threshold;
   }
}
