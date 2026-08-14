package net.minecraft.server.dialog;

import com.mojang.serialization.MapCodec;
import com.mojang.serialization.codecs.RecordCodecBuilder;
import com.mojang.serialization.codecs.RecordCodecBuilder.Instance;
import java.util.List;
import java.util.Optional;
import net.minecraft.util.ExtraCodecs;

public record MultiActionDialog(CommonDialogData common, List<ActionButton> actions, Optional<ActionButton> exitAction, int columns)
    implements ButtonListDialog {
    public static final MapCodec<MultiActionDialog> MAP_CODEC = RecordCodecBuilder.mapCodec(
        p_410561_ -> p_410561_.group(
                CommonDialogData.MAP_CODEC.forGetter(MultiActionDialog::common),
                ExtraCodecs.nonEmptyList(ActionButton.CODEC.listOf()).fieldOf("actions").forGetter(MultiActionDialog::actions),
                ActionButton.CODEC.optionalFieldOf("exit_action").forGetter(MultiActionDialog::exitAction),
                ExtraCodecs.POSITIVE_INT.optionalFieldOf("columns", 2).forGetter(MultiActionDialog::columns)
            )
            .apply(p_410561_, MultiActionDialog::new)
    );

    @Override
    public MapCodec<MultiActionDialog> codec() {
        return MAP_CODEC;
    }

    @Override
    public CommonDialogData common() {
        return this.common;
    }

    @Override
    public Optional<ActionButton> exitAction() {
        return this.exitAction;
    }

    @Override
    public int columns() {
        return this.columns;
    }
}
