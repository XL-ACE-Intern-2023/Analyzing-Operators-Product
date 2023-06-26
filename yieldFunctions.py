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
        return
    
    def _generate_yield_data(self, data_yield):
        yield_product = []
        for i in range(len(data_yield['Operator'])):
            price = data_yield['Harga'].values[i] * 1000
            quota = data_yield['Kuota Utama (GB)'].values[i] + data_yield['Kuota Aplikasi (GB)'].values[i] + \
                    data_yield['Fair Usage Policy (GB)'].values[i]
            validity = data_yield['Masa Berlaku (Hari)'].values[i]
            yield_formula = price / (quota * validity)
            yield_product.append(round(yield_formula, 2))
        data_yield['Yield ((Rp/GB)/Hari)'] = yield_product

        return data_yield

    def _non_apps_yield_data(self, raw_clustered):
        yield_product = []
        for i in range(len(raw_clustered['Operator'])):
            price = raw_clustered['Harga'].values[i] * 1000
            quota = raw_clustered['Kuota Utama (GB)'].values[i] + \
                    raw_clustered['Fair Usage Policy (GB)'].values[i]
            validity = raw_clustered['Masa Berlaku (Hari)'].values[i]
            yield_formula = price / (quota * validity)
            yield_product.append(round(yield_formula, 2))
        raw_clustered['Yield Non-Apps ((Rp/GB)/Hari)'] = yield_product
        
        return raw_clustered

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
            title = f"Main, Unlimited, and Application Quota Yield For For Each Operators"        
        elif type == 'non_apps' :
            y = 'Yield Non-Apps ((Rp/GB)/Hari)'
            title = f"Main and Unlimited Quota Yield For Each Operators For Each Operators"
        operators_yield = px.box(
                filtered_yield_data,
                x="Operator",
                y=y,
                color='Operator',
                category_orders = self.operator_in_order,
                color_discrete_map = self.discrete_color)
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
            color_discrete_map = self.discrete_color)
        cluster_yield = self.set_figure(cluster_yield, title)

        return cluster_yield