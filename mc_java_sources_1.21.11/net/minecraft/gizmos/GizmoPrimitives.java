package net.minecraft.gizmos;

import net.minecraft.world.phys.Vec3;

public interface GizmoPrimitives {
    void addPoint(Vec3 p_460598_, int p_452641_, float p_453479_);

    void addLine(Vec3 p_459401_, Vec3 p_459700_, int p_459579_, float p_455557_);

    void addTriangleFan(Vec3[] p_458799_, int p_450406_);

    void addQuad(Vec3 p_459697_, Vec3 p_451370_, Vec3 p_460506_, Vec3 p_450868_, int p_455763_);

    void addText(Vec3 p_455174_, String p_460500_, TextGizmo.Style p_456654_);
}
