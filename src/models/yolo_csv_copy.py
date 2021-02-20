import pandas as pd
import math
import sys

"""
Doc Doc Doc


Notes:

Split occurs when multiple objs exist in same trap and share the same predeccorID?
Ask about Trap #4 (and how traps are related).
"""

class YoloCSV:

    def __init__(self, file_path):
        self.file_path = file_path
        self.df = None
        self._on_init()

    def _on_init(self):
        self.df = pd.read_csv(self.file_path)

    def describe_all(self):
        """
        Currently not used.

        Just getting familiar w/ the data/taking a look at various relationships.

        Some notes
        trap_num:
        time_num:
        total_objs: total number of cells in the image
        predecessorID: label ID for each cell in each image for tracking
        """

        print("Head")
        print(self.df.head())
        print("Unique K/V")
        for k in self.df.columns:
            u_v = self.df[k].unique()
            print(k, len(u_v), u_v)

        for trap in self.df["trap_num"].unique():
            pred_ids = self.df.query("trap_num == {}".format(trap))["predecessorID"].unique()
         #   print(trap, pred_ids)

    def describe_trap(self, trap_num, t_start=None, t_stop=None, pred_id=None):
        """
        Currently not used.

        Queries a specific trap. Optional args from narrowing down time period and pred_id

        -- Mostly replaced w/ self.query(), prob change this to something else
        """

        t_start = self.df["time_num"].min() if not t_start else t_start
        t_stop = self.df["time_num"].max() if not t_stop else t_stop

        query = "trap_num == {} and {} <= time_num <= {}".format(trap_num, t_start, t_stop)
        if pred_id:
            query += " and predecessorID == {}".format(pred_id)
        df = self.df.query(query)
        for i, v in df.iterrows():
            print(v)

        print(len(df.index))

    def query(self, trap_num=None, t_start=None, t_stop=None, total_objs=None, pred_id=None, write_csv=False):
        """
        Easy way to query the full .csv/df.
        """

        query = ""

        if trap_num:
            query += "trap_num == {}".format(trap_num)

        if t_start and t_stop:
            query += " and {} <= time_num <= {}".format(t_start, t_stop)
        else:
            if t_start:
                query += " and time_num >= {}".format(t_start)
            if t_stop:
                query += " and time_num <= {}".format(t_stop)

        if total_objs:
            query += " and total_objs == {}".format(total_objs)

        if pred_id:
            query += " and predecessorID == {}".format(pred_id)

        if query[0] == " ":
            query = query[5:]

        res = self.df.query(query)

        if write_csv:
            res.to_csv("data/recent_query.csv", index=False)

        return res

    def to_graph_dict(self, trap_num, t_stop):
        """
        Attempts to parse a yolo.csv into a tree data structure that can then be used for further analysis.
        Good amount of in-line doc to cover how its done.

        Note: Currently not safe for all scenarios. Built using only trap == 1 w/ t_stop of ~30. Will likely need
        to re-write a good deal, but wanted to get something up and going that could be used with some visual tools
        before continuing.
        """

        graph_dict = {}

        # Return a copy of the source data filtered to specific trap number and t_stop.
        df = self.query(trap_num=trap_num, t_start=0, t_stop=t_stop, write_csv=True)

        # Some variables used in parsing the above df.
        last_node_name = None
        last_branch_node_name = None
        last_branch_pred_id = None

        # We are interested in changes that occur between time steps. So will create sub-df's using those times.
        for t in df["time_num"].unique():

            # Run another filter of our initial filtered df from above on loop time step.
            time_df = df.query("time_num == {}".format(t))

            # The number of data points per time-step dictates behavior.
            len_time_step = len(time_df.index)

            # Length of 1 indicates no branching and/or start.
            if len_time_step == 1:

                # Basically gets this "row" into a dictionary.
                val = time_df.to_dict('records')[0]
                pred_id = val["predecessorID"]
                time_num = val["time_num"]

                # Edge-case for 1st row. No Pred ID/isNan for that. Assumption that is can be hard-coded to 1. ASK.
                if math.isnan(pred_id):
                    pred_id = 1

                # Node name is time_num.pred_id
                node_name = "{}.{}".format(int(time_num), int(pred_id))

                # Create entry for this node_name in our graph_dict.
                graph_dict[node_name] = []

                # Check if previous node, attach to that if found. Assumes if 1 previous and 1 current, this is an
                # extension of the main branch. ASK.
                if last_node_name:
                    graph_dict[node_name].append(last_node_name)
                    graph_dict[last_node_name].append(node_name)

                # Set last_node_name to current. Continue to next time_step
                last_node_name = node_name
                continue

            # Branching. len_time_step != 1, so there are multiple data points at this step.
            # First lets see if both data points share the same values.
            step_info = time_df.to_dict('records')
            step_info = [[step_info[k] for k in step_info] for step_info in step_info]
            step_info = [list(x) for x in set(tuple(x) for x in step_info)]

            #TODO: FOR 130 Bug, looks like need to check above logic, possible that a new branch can be created, and
            # stuff gets added etc, in same step w/ 3. So step info would be 3, set() would make 2, then 1 of those
            # would be start of new branch, other would main/daughter updating etc.

            # If step_info == 1, both data points are the same. We only need 1. This represents the start of new branch.
            # NOTE: Logic here may fail later on w/ branching occurring in branches... Will need to revisit...
            if len(step_info) == 1:

                # Similar logic to above. (len_time_step == 1).
                val = time_df.to_dict('records')[0]
                pred_id = val["predecessorID"]
                time_num = val["time_num"]
                node_name = "{}.{}".format(int(time_num), int(pred_id))
                graph_dict[node_name] = []
                if last_node_name:
                    graph_dict[node_name].append(last_node_name)
                    graph_dict[last_node_name].append(node_name)

                last_node_name = node_name

                # Track where this branch started on the main branch. Continue to next time_step.
                last_branch_node_name = node_name
                last_branch_pred_id = pred_id
                continue

            # Multiple unique data points exist at this time step. So both main and daughter branches will update.
            # NOTE: As above, logic here may fail later on w/ branching occurring in branches... Will need to revisit...
            for i, val in time_df.iterrows():

                pred_id = val["predecessorID"]
                time_num = val["time_num"]
                node_name = "{}.{}".format(int(time_num), int(pred_id))

                # Checks to see if continuation of main branch, else daughter branch.
                if pred_id == last_branch_pred_id:
                    graph_dict[node_name] = []
                    graph_dict[node_name].append(last_node_name)
                    graph_dict[last_node_name].append(node_name)
                    last_node_name = node_name
                else:
                    graph_dict[node_name] = []
                    graph_dict[node_name].append(last_branch_node_name)
                    graph_dict[last_branch_node_name].append(node_name)
                    last_branch_node_name = node_name

        print(graph_dict)
        return graph_dict, {"trap_num": trap_num, "t_stop": t_stop}  # Will prob clean this up, but this was quick..