package net.minecraft.world.waypoints;

public interface WaypointManager<T extends Waypoint> {
    void trackWaypoint(T p_406177_);

    void updateWaypoint(T p_410366_);

    void untrackWaypoint(T p_408468_);
}
