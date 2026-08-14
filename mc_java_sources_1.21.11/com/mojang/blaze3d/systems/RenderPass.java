package com.mojang.blaze3d.systems;

import com.mojang.blaze3d.DontObfuscate;
import com.mojang.blaze3d.buffers.GpuBuffer;
import com.mojang.blaze3d.buffers.GpuBufferSlice;
import com.mojang.blaze3d.pipeline.RenderPipeline;
import com.mojang.blaze3d.textures.GpuSampler;
import com.mojang.blaze3d.textures.GpuTextureView;
import com.mojang.blaze3d.vertex.VertexFormat;
import java.util.Collection;
import java.util.function.BiConsumer;
import java.util.function.Supplier;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
@DontObfuscate
public interface RenderPass extends AutoCloseable {
    void pushDebugGroup(Supplier<String> p_408185_);

    void popDebugGroup();

    void setPipeline(RenderPipeline p_394712_);

    void bindTexture(String p_395678_, @Nullable GpuTextureView p_406805_, @Nullable GpuSampler p_453654_);

    void setUniform(String p_394004_, GpuBuffer p_408232_);

    void setUniform(String p_397813_, GpuBufferSlice p_409190_);

    void enableScissor(int p_392594_, int p_394512_, int p_391828_, int p_391712_);

    void disableScissor();

    void setVertexBuffer(int p_393394_, GpuBuffer p_395764_);

    void setIndexBuffer(GpuBuffer p_393127_, VertexFormat.IndexType p_397465_);

    void drawIndexed(int p_393708_, int p_396477_, int p_409446_, int p_407636_);

    <T> void drawMultipleIndexed(
        Collection<RenderPass.Draw<T>> p_392442_,
        @Nullable GpuBuffer p_396172_,
        VertexFormat.@Nullable IndexType p_394399_,
        Collection<String> p_406241_,
        T p_406608_
    );

    void draw(int p_397730_, int p_394941_);

    @Override
    void close();

    @OnlyIn(Dist.CLIENT)
    public record Draw<T>(
        int slot,
        GpuBuffer vertexBuffer,
        @Nullable GpuBuffer indexBuffer,
        VertexFormat.@Nullable IndexType indexType,
        int firstIndex,
        int indexCount,
        @Nullable BiConsumer<T, RenderPass.UniformUploader> uniformUploaderConsumer
    ) {
        public Draw(int p_394209_, GpuBuffer p_394761_, GpuBuffer p_393439_, VertexFormat.IndexType p_393418_, int p_392985_, int p_394886_) {
            this(p_394209_, p_394761_, p_393439_, p_393418_, p_392985_, p_394886_, null);
        }
    }

    @OnlyIn(Dist.CLIENT)
    public interface UniformUploader {
        void upload(String p_391168_, GpuBufferSlice p_407704_);
    }
}
