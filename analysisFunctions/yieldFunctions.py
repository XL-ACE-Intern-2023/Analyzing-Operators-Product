import warnings
import plotly.express as px

warnings.simplefilter("ignore")

class yield_functions:
    def __init__(self):
        self.scale_color = 'inferno'
        self.discrete_color = {"AXIS" : "#6F2791", 
                                "XL" : "#01478F", 
                                "Telkomsel" : "#ED0226",
                                "Indosat" : "#FFD600",
                                "Smartfren" : "#FF1578",
                                "Tri" : "#9E1F64"}
        self.operator_in_order = {'Operator':['XL', 'Telkomsel', 'Indosat', 'AXIS', 'Tri', 'Smartfren']}
        self.cluster_in_order = {'Cluster Label' :[ 'High Main (1)',
                                                   'Medium Main (2)',
                                                   'Low Main (3)',
                                                   'Low Unlimited (4)',
                                                   'High Unlimited (5)',
                                                   '80:20 High Main and App (6)',
                                                   '50:50 Low Main and App (7)','20:80 Medium Main and App (8)']}
        return
    

    def set_figure(self, fig, title, title_size=28, font_size=20):
        fig.update_layout(title=title ,title_font_size=title_size)
        fig.update_layout(
            font=dict(
                family="Courier",
                size=font_size, 
                color="black"
            ))
        fig.update_xaxes(linewidth=2, tickfont_size=20, title_font_size=25)
        fig.update_yaxes(tickfont_size=20,title_font_size=25)

        return fig

    def _visualize_operators_yield(self, filtered_yield_data, type):
        if type == 'apps' :
            y = 'Yield ((Rp/GB)/Hari)'
            title = f"Main, Unlimited, and Application Quota Yield For Each Operators"        
        elif type == 'non_apps' :
            y = 'Yield Non-Apps ((Rp/GB)/Hari)'
            title = f"Main and Unlimited Quota Yield For Each Operators For Each Operators"
        operators_yield = px.box(
                filtered_yield_data,
                x="Operator",
                y=y,
                color='Operator',
                category_orders = self.operator_in_order,
                color_discrete_map = self.discrete_color,
                height = 500)
        operators_yield = self.set_figure(operators_yield, title)

        return operators_yield
   
    def _visualize_cluster_yield(self, filtered_yield_data, cluster, type, label):
        if type == 'apps':
            y = 'Yield ((Rp/GB)/Hari)'
            title = f"Main, Unlimited, and Application Quota Yield For {label} Product"
        elif type == 'non-apps':
            y = 'Yield Non-Apps ((Rp/GB)/Hari)'
            title = f"Main and Unlimited Quota Yield For Each Operators For {label} Product"
        cluster_yield = px.box(
            filtered_yield_data.loc[filtered_yield_data['Cluster']==cluster],
            x='Operator',
            y=y,
            color="Operator", 
            category_orders = self.operator_in_order,
            color_discrete_map = self.discrete_color,
            height = 500)
        cluster_yield = self.set_figure(cluster_yield, title)

        return cluster_yield
    
    def _visualize_all_cluster_yield(self, filtered_yield_data, type):
        if type == 'apps' :
            y = 'Yield ((Rp/GB)/Hari)'
            title = f"Main, Unlimited, and Application Quota Yield For Each Clusters"        
        elif type == 'non_apps' :
            y = 'Yield Non-Apps ((Rp/GB)/Hari)'
            title = f"Main and Unlimited Quota Yield For Each Operators For Each Clusters"
        operators_yield = px.box(
                filtered_yield_data,
                x="Cluster Label",
                y=y,
                color="Cluster Label",
                category_orders = self.cluster_in_order,
                color_discrete_map = self.discrete_color,
                height = 800)
        operators_yield = self.set_figure(operators_yield, title)

        return operators_yield
