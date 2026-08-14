package net.minecraft.client.renderer;

import com.mojang.blaze3d.vertex.PoseStack;
import java.util.List;
import net.minecraft.client.gui.Font;
import net.minecraft.client.model.Model;
import net.minecraft.client.model.geom.ModelPart;
import net.minecraft.client.renderer.block.MovingBlockRenderState;
import net.minecraft.client.renderer.block.model.BakedQuad;
import net.minecraft.client.renderer.block.model.BlockStateModel;
import net.minecraft.client.renderer.entity.state.EntityRenderState;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.item.ItemStackRenderState;
import net.minecraft.client.renderer.rendertype.RenderType;
import net.minecraft.client.renderer.state.CameraRenderState;
import net.minecraft.client.renderer.texture.TextureAtlasSprite;
import net.minecraft.network.chat.Component;
import net.minecraft.util.FormattedCharSequence;
import net.minecraft.world.item.ItemDisplayContext;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.phys.Vec3;
import net.minecraftforge.api.distmarker.Dist;
import net.minecraftforge.api.distmarker.OnlyIn;
import org.joml.Quaternionf;
import org.jspecify.annotations.Nullable;

@OnlyIn(Dist.CLIENT)
public interface OrderedSubmitNodeCollector {
    void submitShadow(PoseStack p_424536_, float p_427376_, List<EntityRenderState.ShadowPiece> p_425805_);

    void submitNameTag(
        PoseStack p_430309_,
        @Nullable Vec3 p_426805_,
        int p_429735_,
        Component p_429394_,
        boolean p_426383_,
        int p_424984_,
        double p_422348_,
        CameraRenderState p_430823_
    );

    void submitText(
        PoseStack p_425661_,
        float p_431152_,
        float p_426218_,
        FormattedCharSequence p_425580_,
        boolean p_430286_,
        Font.DisplayMode p_429691_,
        int p_427899_,
        int p_429916_,
        int p_425142_,
        int p_424806_
    );

    void submitFlame(PoseStack p_427290_, EntityRenderState p_426060_, Quaternionf p_428897_);

    void submitLeash(PoseStack p_426212_, EntityRenderState.LeashState p_427424_);

    <S> void submitModel(
        Model<? super S> p_424063_,
        S p_430077_,
        PoseStack p_426090_,
        RenderType p_454658_,
        int p_424302_,
        int p_429131_,
        int p_424675_,
        @Nullable TextureAtlasSprite p_456949_,
        int p_458231_,
        ModelFeatureRenderer.@Nullable CrumblingOverlay p_427640_
    );

    default <S> void submitModel(
        Model<? super S> p_423531_,
        S p_423172_,
        PoseStack p_430909_,
        RenderType p_452425_,
        int p_429653_,
        int p_427844_,
        int p_429198_,
        ModelFeatureRenderer.@Nullable CrumblingOverlay p_428470_
    ) {
        this.submitModel(p_423531_, p_423172_, p_430909_, p_452425_, p_429653_, p_427844_, -1, null, p_429198_, p_428470_);
    }

    default void submitModelPart(ModelPart p_428756_, PoseStack p_425252_, RenderType p_460672_, int p_427164_, int p_422744_, @Nullable TextureAtlasSprite p_425811_) {
        this.submitModelPart(p_428756_, p_425252_, p_460672_, p_427164_, p_422744_, p_425811_, false, false, -1, null, 0);
    }

    default void submitModelPart(
        ModelPart p_422542_,
        PoseStack p_423411_,
        RenderType p_457471_,
        int p_430083_,
        int p_423063_,
        @Nullable TextureAtlasSprite p_430651_,
        int p_453977_,
        ModelFeatureRenderer.@Nullable CrumblingOverlay p_453259_
    ) {
        this.submitModelPart(p_422542_, p_423411_, p_457471_, p_430083_, p_423063_, p_430651_, false, false, p_453977_, p_453259_, 0);
    }

    default void submitModelPart(
        ModelPart p_428070_,
        PoseStack p_431622_,
        RenderType p_460296_,
        int p_424143_,
        int p_431591_,
        @Nullable TextureAtlasSprite p_425071_,
        boolean p_454543_,
        boolean p_450949_
    ) {
        this.submitModelPart(p_428070_, p_431622_, p_460296_, p_424143_, p_431591_, p_425071_, p_454543_, p_450949_, -1, null, 0);
    }

    void submitModelPart(
        ModelPart p_430617_,
        PoseStack p_426460_,
        RenderType p_454113_,
        int p_425933_,
        int p_427082_,
        @Nullable TextureAtlasSprite p_422840_,
        boolean p_451042_,
        boolean p_459722_,
        int p_422451_,
        ModelFeatureRenderer.@Nullable CrumblingOverlay p_429727_,
        int p_459251_
    );

    void submitBlock(PoseStack p_426458_, BlockState p_424829_, int p_431608_, int p_426712_, int p_430533_);

    void submitMovingBlock(PoseStack p_428761_, MovingBlockRenderState p_430963_);

    void submitBlockModel(
        PoseStack p_430233_,
        RenderType p_459801_,
        BlockStateModel p_429985_,
        float p_425290_,
        float p_427242_,
        float p_425256_,
        int p_425221_,
        int p_424481_,
        int p_431191_
    );

    void submitItem(
        PoseStack p_426697_,
        ItemDisplayContext p_427934_,
        int p_428737_,
        int p_431597_,
        int p_423167_,
        int[] p_429176_,
        List<BakedQuad> p_430385_,
        RenderType p_455290_,
        ItemStackRenderState.FoilType p_429937_
    );

    void submitCustomGeometry(PoseStack p_427731_, RenderType p_454861_, SubmitNodeCollector.CustomGeometryRenderer p_426220_);

    void submitParticleGroup(SubmitNodeCollector.ParticleGroupRenderer p_423310_);
}
