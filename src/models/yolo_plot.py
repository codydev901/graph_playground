import plotly.graph_objects as go
import sys
import math

"""

XN [-1.0, -1.0, -1.0, -1.0, 0.0, 0.0, 1.0, 0.0, 1.0]
Yn [4.0, 5.0, 6.0, 7.0, 8.0, 7.0, 7.0, 6.0, 6.0]
traces ['1.1', '2.1', '3.1', '4.1', '5.1', '6.1', '6.2', '7.1', '7.2']

fig.add_trace(go.Scatter(x=Xn,
                             y=Yn,
                             mode='markers',
                             name='bla',
                             marker=dict(symbol='circle-dot',
                                         size=18,
                                         color='#6175c1',  # '#DB4551',
                                         line=dict(color='rgb(50,50,50)', width=1)
                                         ),
                             text=labels,
                             hoverinfo='text',
                             opacity=0.8
                             ))
                             
could try shapes https://plotly.com/python/shapes/?                            
"""


class YoloPlot:

    def __init__(self, yolo_tree, graph_info):
        self.yolo_tree = yolo_tree
        self.graph_info = graph_info
        self.fig = go.Figure()
        self.plot_info = {}
        self._on_init()

    def _on_init(self):
        """
        Doc Doc Doc
        """

        self._plot_info_from_tree_dict()
        self.fig.update_xaxes(range=[0.0, float(self.plot_info["x_bound"])])
        self.fig.update_yaxes(range=[0.0, float(self.plot_info["y_bound"])])
        self.fig.layout.title["text"] = "TrapNum:{} TStop:{}".format(self.graph_info["trap_num"],
                                                                     self.graph_info["t_stop"])

        # Root Node Position(s)
        self.plot_info["root_pos"] = {}
        self._establish_root_positions()

        # Main Branch Lines(s)
        main_trace = self._get_main_branch_traces()
        self.add_trace(main_trace, mode="lines")

        # Daughter Branch Lines(s)
        daughter_trace = self._get_daughter_branch_traces()
        for d_t in daughter_trace:
            self.add_trace(d_t, mode="lines")

        # Branch and Leaf Points
        branch_leaf_points = self._get_branch_leaf_points(daughter_trace)
        for b_p in branch_leaf_points:
            self.add_trace(b_p, mode="markers+text", size=32)

        # # Time Num Obj
        time_num_obj_trace = self._get_time_num_traces()
        self.add_trace(time_num_obj_trace, symbol="square", mode="text", size=36)

    def _plot_info_from_tree_dict(self):
        """
        Doc Doc Doc
        """

        # To Establish X Bounds, check for max length of main branches
        max_main_branch_length = 0
        for n in self.yolo_tree.tree_info["root_nodes"]:
            main_branch_length = len(self.yolo_tree.tree_dict[n])
            if main_branch_length > max_main_branch_length:
                max_main_branch_length = main_branch_length

        # To Establish Y bounds, check for max length of daughter branches
        daughter_nodes = [n for n in self.yolo_tree.tree_dict if n not in self.yolo_tree.tree_info["root_nodes"]]
        max_daughter_branch_length = 0
        for n in daughter_nodes:
            daughter_branch_length = len(self.yolo_tree.tree_dict[n])
            if daughter_branch_length > max_daughter_branch_length:
                max_daughter_branch_length = daughter_branch_length

        self.plot_info["x_bound"] = max_main_branch_length + 2
        self.plot_info["y_bound"] = (max_daughter_branch_length + 2) * 2

    def _establish_root_positions(self):
        """
        Doc Doc Doc
        """

        num_root = len(self.yolo_tree.tree_info["root_nodes"])
        y_offset = self.plot_info["y_bound"] / (num_root+1)
        for i, n in enumerate(self.yolo_tree.tree_info["root_nodes"]):
            x = float(n.split(".", 1)[0])
            y = (i+1)*y_offset   # Fix this when multiple root nodes...
            self.plot_info["root_pos"][n] = {"x": x, "y": y}

    def _get_main_branch_traces(self):
        """
        Doc Doc Doc
        """

        x_arr = []
        y_arr = []
        labels = []

        # Add Root Node
        for r_n in self.yolo_tree.tree_info["root_nodes"]:
            x = self.plot_info["root_pos"][r_n]["x"]
            y = self.plot_info["root_pos"][r_n]["y"]
            x_arr.append(x)
            y_arr.append(y)
            labels.append(r_n)
            # Add Continuous Nodes
            for n in self.yolo_tree.tree_dict[r_n]:
                x = float(n.split(".", 1)[0])
                y = self.plot_info["root_pos"][r_n]["y"]
                x_arr.append(x)
                y_arr.append(y)
                labels.append(n)

        return {"x": x_arr, "y": y_arr, "labels": labels, "color": "#008000", "name": "mC"}

    def _get_nodes_of_interest(self):
        """
        WIP
        """

        traces = []

        # Root Nodes
        for r_n in self.yolo_tree.tree_info["root_nodes"]:
            x = self.plot_info["root_pos"][r_n]["x"]
            y = self.plot_info["root_pos"][r_n]["y"]
            label = r_n
            traces.append({"x": [x], "y": [y], "labels": [label], "color": "#008000", "name": "mC"})

        # Branching Nodes
        for b_n in self.yolo_tree.tree_info["branch_edges"]:
            parent = b_n[0]
            daughter = b_n[0]   # Branch edges goes from 5.1 -> 6.2 atm, but we want to go from 5.1 -> 5.2 -> 6.2
            daughter = parent.split(".", 1)[0] + "." + daughter.split(".", 1)[-1]

        pass

    def _get_daughter_branch_traces(self):
        """
        Doc Doc Doc
        """

        y_multiplier = 1  # Visually nicer, alternates branches...

        # print("AHHH")
        # print(self.plot_info)

        all_res = []

        for d_n in self.yolo_tree.tree_dict:

            x_arr = []
            y_arr = []
            labels = []

            if d_n in self.yolo_tree.tree_info["root_nodes"]:
                continue

            # Find node in main branch where daughter node connects
            main_daughter_edge = list(filter(lambda x: x[1] == d_n, self.yolo_tree.tree_info["branch_edges"]))[0]

            # print("MAIN DAUGHTER EDGE")
            # print(main_daughter_edge)

            # Get Y-val of that main branch by finding the root node of the parent edge node
            main_root_node_y = None
            for r_n in self.yolo_tree.tree_dict:
                if main_daughter_edge[0] in self.yolo_tree.tree_dict[r_n]:
                    try:
                        main_root_node_y = self.plot_info["root_pos"][r_n]["y"]
                    except KeyError as e:
                        print("BROKE YOLOPLOT 147")
                        print(e)
                        print(d_n)
                        print(main_daughter_edge)
                        sys.exit()
                    break

            # Add a point for the parent/daughter connection
            x = int(main_daughter_edge[0].split(".", 1)[0])
            y = main_root_node_y
            x_arr.append(x)
            y_arr.append(y)
            labels.append(main_daughter_edge[0])

            # Y Branch Offset
            y_branch_offset = (self.plot_info["y_bound"] - main_root_node_y) / 2

            # Add edge_node of daughter branch (technically root, but not stored that way in tree, created here)
            x = float(main_daughter_edge[0].split(".", 1)[0])
            y = main_root_node_y + (y_branch_offset * y_multiplier)
            x_arr.append(x)
            y_arr.append(y)
            labels.append("{}.{}".format(main_daughter_edge[0].split(".")[0], main_daughter_edge[1].split(".")[1]))

            # Add root of daughter branch
            x = float(main_daughter_edge[1].split(".", 1)[0])
            y = main_root_node_y + (y_branch_offset * y_multiplier)
            x_arr.append(x)
            y_arr.append(y)
            labels.append(d_n)

            # print("ROOT DAUGHTER")
            # print(x, y, d_n)
            #
            # Add nodes in daughter branch
            for i, n in enumerate(self.yolo_tree.tree_dict[d_n]):
                i += 1
                x = float(main_daughter_edge[1].split(".", 1)[0]) + i
                y = main_root_node_y + (y_branch_offset * y_multiplier)
                x_arr.append(x)
                y_arr.append(y)
                labels.append(n)
                # print("BRANCH DAUGHTER")
                # print(x, y, n)

            y_multiplier *= -1

            all_res.append({"x": x_arr, "y": y_arr, "labels": labels, "color": "#FFA500", "name": "dC"})

        return all_res

    def _get_branch_leaf_points(self, daughter_traces):
        """
        Doc Doc Doc
        """

        res = []

        for d_t in daughter_traces:
            x_arr = []
            y_arr = []
            labels = []
            # Parent Point
            x_arr += [d_t["x"][0]]
            y_arr += [d_t["y"][0]]
            labels += [d_t["labels"][0]]
            # Daughter Point
            x_arr += [d_t["x"][1]]
            y_arr += [d_t["y"][1]]
            labels += [d_t["labels"][1]]
            # Leaf Point
            x_arr += [d_t["x"][-1]]
            y_arr += [d_t["y"][-1]]
            labels += [d_t["labels"][-1]]

            res.append({"x": x_arr, "y": y_arr, "labels": labels, "color": "#FFA500", "name": "dC"})

        return res

    def _get_time_num_traces(self):
        """
        Doc Doc Doc
        """

        x_arr = []
        y_arr = []
        labels = []

        for t_n in self.graph_info["time_num_obj"]:

            x = float(t_n[0])
            y = 1.0
            x_arr.append(x)
            y_arr.append(y)
            labels.append(t_n[1])

        return {"x": x_arr, "y": y_arr, "labels": labels, "color": "#008000", "name": "mC"}

    def add_trace(self, trace_info, symbol=None, size=None, mode=None):
        """
        Doc Doc Doc
        """
        # Might clean this up, but wanted to play around.
        if not symbol:
            symbol = "circle"
        if not size:
            size = None
        if not mode:
            mode = "markers"

        self.fig.add_trace(go.Scatter(x=trace_info["x"],
                                      y=trace_info["y"],
                                      mode=mode,
                                      name=trace_info["name"],
                                      marker=dict(symbol=symbol,
                                                  size=size,
                                                  color=trace_info["color"],
                                                  line=dict(color='rgb(0,0,0)', width=0.5)
                                                  ),
                                      text=trace_info["labels"],
                                      textfont=dict(color='#000000'),
                                      hoverinfo='text',
                                      opacity=0.8
                                      ))


    def show(self):

        self.fig.show()
