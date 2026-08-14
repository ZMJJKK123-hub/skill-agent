package net.minecraft.util;

import com.mojang.serialization.DataResult;
import com.mojang.serialization.DynamicOps;
import com.mojang.serialization.Lifecycle;
import com.mojang.serialization.ListBuilder;
import java.util.function.UnaryOperator;

abstract class AbstractListBuilder<T, B> implements ListBuilder<T> {
    private final DynamicOps<T> ops;
    protected DataResult<B> builder = DataResult.success(this.initBuilder(), Lifecycle.stable());

    protected AbstractListBuilder(DynamicOps<T> p_393370_) {
        this.ops = p_393370_;
    }

    @Override
    public DynamicOps<T> ops() {
        return this.ops;
    }

    protected abstract B initBuilder();

    protected abstract B append(B p_397540_, T p_392540_);

    protected abstract DataResult<T> build(B p_393055_, T p_392422_);

    @Override
    public ListBuilder<T> add(T p_392714_) {
        this.builder = this.builder.map(p_397872_ -> this.append((B)p_397872_, p_392714_));
        return this;
    }

    @Override
    public ListBuilder<T> add(DataResult<T> p_395150_) {
        this.builder = this.builder.apply2stable(this::append, p_395150_);
        return this;
    }

    @Override
    public ListBuilder<T> withErrorsFrom(DataResult<?> p_392818_) {
        this.builder = this.builder.flatMap(p_394538_ -> p_392818_.map(p_395945_ -> p_394538_));
        return this;
    }

    @Override
    public ListBuilder<T> mapError(UnaryOperator<String> p_393579_) {
        this.builder = this.builder.mapError(p_393579_);
        return this;
    }

    @Override
    public DataResult<T> build(T p_394777_) {
        DataResult<T> dataresult = this.builder.flatMap(p_397770_ -> this.build((B)p_397770_, p_394777_));
        this.builder = DataResult.success(this.initBuilder(), Lifecycle.stable());
        return dataresult;
    }
}
