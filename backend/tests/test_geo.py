from app.geo.grid import create_grid


def test_grid_creation():
    grid = create_grid(0, 0, 0.03, 0.02, 0.01)
    assert len(grid) == 6
    assert grid[0].cell_id == "g_0_0"
