from models.goal import (
    add_goal,
    delete_goal,
    get_goal,
    goal_progress_summary,
    list_goals,
    update_goal,
    update_goal_progress,
)


def test_add_and_get_goal(conn):
    goal = add_goal(
        conn,
        name="Emergency Fund",
        type="savings",
        target=10000.0,
        current=2500.0,
        deadline="2025-12-31",
    )
    assert goal["name"] == "Emergency Fund"
    assert goal["type"] == "savings"
    assert goal["target"] == 10000.0
    assert goal["current"] == 2500.0
    assert goal["active"] == 1

    fetched = get_goal(conn, goal["id"])
    assert fetched == goal


def test_get_goal_missing(conn):
    assert get_goal(conn, 999) is None


def test_list_goals_active_only(conn):
    active = add_goal(conn, "Vacation", "savings", 5000.0)
    add_goal(conn, "Old Goal", "savings", 1000.0, active=0)

    active_only = list_goals(conn, active_only=True)
    assert len(active_only) == 1
    assert active_only[0]["id"] == active["id"]

    all_goals = list_goals(conn, active_only=False)
    assert len(all_goals) == 2


def test_update_goal_only_changes_passed_fields(conn):
    goal = add_goal(
        conn,
        name="Emergency Fund",
        type="savings",
        target=10000.0,
        current=2500.0,
        notes="high priority",
    )
    updated = update_goal(conn, goal["id"], current=3000.0)
    assert updated["current"] == 3000.0
    assert updated["name"] == "Emergency Fund"
    assert updated["target"] == 10000.0
    assert updated["notes"] == "high priority"


def test_update_goal_missing(conn):
    assert update_goal(conn, 999, current=100.0) is None


def test_update_goal_progress(conn):
    goal = add_goal(conn, "Vacation", "savings", 5000.0, current=1000.0)
    updated = update_goal_progress(conn, goal["id"], 1500.0)
    assert updated["current"] == 1500.0


def test_delete_goal(conn):
    goal = add_goal(conn, "Test Goal", "savings", 1000.0)
    assert delete_goal(conn, goal["id"]) is True
    assert get_goal(conn, goal["id"]) is None
    assert delete_goal(conn, goal["id"]) is False


def test_goal_progress_summary(conn):
    add_goal(conn, "Half Done", "savings", 1000.0, current=500.0)
    add_goal(conn, "Complete", "investment", 2000.0, current=2000.0)
    add_goal(conn, "Not Started", "spending_limit", 500.0, current=0.0)
    add_goal(conn, "Inactive", "savings", 1000.0, current=100.0, active=0)

    summary = goal_progress_summary(conn)
    assert len(summary) == 3

    by_name = {s["name"]: s for s in summary}
    assert by_name["Half Done"]["progress_pct"] == 50.0
    assert by_name["Complete"]["progress_pct"] == 100.0
    assert by_name["Not Started"]["progress_pct"] == 0.0
