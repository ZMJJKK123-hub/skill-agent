package net.minecraft.world.attribute;

import net.minecraft.world.phys.Vec3;
import org.jspecify.annotations.Nullable;

public sealed interface EnvironmentAttributeLayer<Value>
    permits EnvironmentAttributeLayer.Constant,
    EnvironmentAttributeLayer.TimeBased,
    EnvironmentAttributeLayer.Positional {
    @FunctionalInterface
    public non-sealed interface Constant<Value> extends EnvironmentAttributeLayer<Value> {
        Value applyConstant(Value p_459450_);
    }

    @FunctionalInterface
    public non-sealed interface Positional<Value> extends EnvironmentAttributeLayer<Value> {
        Value applyPositional(Value p_450535_, Vec3 p_459845_, @Nullable SpatialAttributeInterpolator p_457174_);
    }

    @FunctionalInterface
    public non-sealed interface TimeBased<Value> extends EnvironmentAttributeLayer<Value> {
        Value applyTimeBased(Value p_456873_, int p_452357_);
    }
}
