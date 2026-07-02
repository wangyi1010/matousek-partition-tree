# Examples

`points_example.csv` is a tiny 2D point set:

```csv
x,y
0,0
1,2
2,1
...
```

Run the practical baseline:

```bash
python3 ../src/practical_partition_tree_2d.py points_example.csv --r 4 --leaf-size 2 --groups-out groups_example.json --halfplane 1 0 -5
```

The halfplane is:

$$
x-5\ge 0
$$

