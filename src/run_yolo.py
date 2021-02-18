from models.yolo_csv import YoloCSV
from models.yolo_tree import YoloTree
from models.yolo_plot import YoloPlot
from models.i_graph import graph_to_i_graph

"""
Doc Doc Doc

Test Graph
g = {"a": ["d"],
     "b": ["c", "f"],
     "c": ["b", "c", "d", "e"],
     "d": ["a", "c"],
     "e": ["c"],
     "f": [],
    }
"""


def main():

    yolo = YoloCSV("data/FT_BC8_yolo_short.csv")
    graph_dict, yolo_trap_time = yolo.to_graph_dict(trap_num=1, t_stop=110)
    # print("Graph Crashes/Hangs up at Tmax of 50... So need to look into that")
    print(graph_dict)
    print("Tree Start")
    tree = YoloTree(graph_dict)
    print("Tree Dict")
    print(tree.tree_dict)
    print(tree.tree_info)

    plot = YoloPlot(tree, yolo_trap_time)
    plot.show()

    # print(graph.info)

    # graph_to_i_graph(graph_dict)


if __name__ == "__main__":

    main()