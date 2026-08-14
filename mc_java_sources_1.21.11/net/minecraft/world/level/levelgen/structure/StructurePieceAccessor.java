package net.minecraft.world.level.levelgen.structure;

import org.jspecify.annotations.Nullable;

public interface StructurePieceAccessor {
    void addPiece(StructurePiece p_163589_);

    @Nullable StructurePiece findCollisionPiece(BoundingBox p_163588_);
}
