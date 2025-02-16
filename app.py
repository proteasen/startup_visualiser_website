# For easy reference and to deploy to server:
# [Insert your path to folder]: 
# rsconnect deploy shiny "/Path to your folder/myapp" --name padangco --title asean-startups

# structure: 
# - Query (filter functions, no export function and filter only by typing)
# - About Page 
# - Overview 
#   a. Total No. of Startups - Value Box (Done)  
#   b. Top 3 Common Industries - Value Box (Done)
#   c. Top 3 Common Activities - Value Box (Done)  
#   d. Average Founding Year - Heat Map (Done)
# - Industry
#   a. Total No. of Startups - Tree Map (Done)
#   b. Deal Volume and Deal Value 
#   c. By Industry - network diagram (with activity)   
# - Investments  
#   a. Funding Stage (individual) (Done)
#   b. Company Stage by Country - Lollilop Chart (Done)
#   c. Funding Round (no. of deals and amount) by Quarter - Bar Graph (Done)  

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import plotly.express as px
import plotly.graph_objs as go

from pathlib import Path
from shared import app_dir, df, df_additional
from shiny import App, reactive, render
from shiny.express import input, render, ui
from shinywidgets import render_plotly

ui.include_css(app_dir / "styles.css")

ui.page_opts(
    title=ui.img(src="https://images.glints.com/unsafe/160x0/glints-dashboard.s3.amazonaws.com/company-logo/1a6a3a95c565ad1a74ced0c29fecf53e.png", alt="padang & co | southeast asia green economy startup landscape report", height="40px"), 
    fillable=True,
    style= "padding: 20px;"
    )

with ui.sidebar():
    
    ui.input_checkbox_group(
        "Country",
        "Select Country:",
        {
            "Indonesia": "Indonesia",
            "Malaysia": "Malaysia",
            "Philippines": "Philippines",
            "Singapore": "Singapore",
            "Thailand": "Thailand",
            "Vietnam": "Vietnam"
        }
    )

with ui.navset_pill(id="tab"):  

    with ui.nav_panel("About"):
        ui.h2("Southeast Asia Green Economy Report Interactive Website"),
        # ui.div(
        # ui.span("Click "), 
        # ui.tags.a("here", href="https://padang.co", target="_blank"), 
        # ui.span(" to access the report.")
        # ),
        ui.p(" ")
        ui.p("This exclusive Interactive Website serves to complement our Report, allowing viewers to interact and visualise data involving startups in Southeast Asia's Green Economy.")
        ui.p("The website allows viewers to select the Asean-6 Countries and filter the data across Query, Overview, and Industry tabs.")
        ui.p("The Query tab provides viewers with a table list of all startups sourced by Padang & Co. Filter by clicking the title headers or type in the specific information, e.g. minimum and maximum Year.")
        ui.p("The Overview tab provides key figures and visualisations of the startups."),
        ui.p("The Industry tab provides visualisations of the industry and activity breakdowns for all startups.")
        ui.p("The Investment tab provides key figures and visualisations about funding stages for all startups.")
        ui.p("Contact us for more information, such as accessibility issues or finding a startup not listed here.")
        ui.help_text("© 2024 ", ui.tags.a("Padang & Co", href= "https://www.padang.co", target="_blank"), ". Last Updated on 9 September 2024 | ", ui.tags.a(" Terms of Use", href= "https://docs.google.com/document/d/1eKOK9mRKGTQaxSUujuXihTpxGrleD6VY6k169DZA9F0/edit?usp=sharing", target="_blank"))
    
    with ui.nav_panel("Query"):
        with ui.layout_columns():

            with ui.card(full_screen=True):
                ui.card_header("Southeast Asia Green Economy")

                @render.data_frame
                def summary_statistics():

                    cols = [
                        "Industry",
                        "Activity 1",
                        "Activity 2",
                        "Activity 3",
                        "Country",
                        "Company",
                        "Website",
                        "Founded Year",
                        "Company Stage",
                    ]

                    return render.DataGrid(filtered_df()[cols], filters=True)

    with ui.nav_panel("Overview"):

        with ui.layout_column_wrap(fill=False):
            with ui.value_box():
                "Total Number of Startups"
                @render.text
                def count():
                    df_filtered = filtered_df()
                    return df_filtered.shape[0]
                
            @reactive.calc
            def filtered_df():
                selected_country = input.Country()
                selected_stage = input.Stage()
                filt_df = df[df["Country"].isin(selected_country)]
                return filt_df

        with ui.value_box():
            "Top 3 Most Common Industries"
            @render.ui
            def get_most_common_industry():
                df = filtered_df()
                industry_modes = df['Industry'].value_counts()
                return ui.HTML('<br>'.join(list(industry_modes.index[:3])))
            
        @reactive.calc
        def filtered_df():
            filt_df = df[df["Country"].isin(input.Country())]
            return filt_df

        with ui.value_box():
            "Top 3 Most Common Activities"
            @render.ui
            def get_most_common_activity():
                df = filtered_df()
                activity_modes = df['Activity 1'].value_counts()
                return ui.HTML('<br>'.join(list(activity_modes.index[:3]))) 

        @reactive.calc
        def filtered_df():
            filt_df = df[df["Country"].isin(input.Country())]
            return filt_df  

        ui.h4("Founded Year of Startups by Industry")
        @render.plot(alt="Founded Year of Startups")
        def heatmap():
            filt_df = df[df["Country"].isin(input.Country())]  
            heat_map = filt_df.groupby(["Industry", "Founded Year"]).size().unstack(fill_value=0)  

            fig, ax = plt.subplots(figsize=(16, 12))  

            sns.heatmap(heat_map, annot=True, fmt="d", linewidths=.2, ax=ax, cmap="YlGnBu", vmin=0, vmax=30)  

            ax.set_title("")
            ax.set_xlabel("Founded Year")
            ax.set_ylabel("Industry")

            return fig

    with ui.nav_panel("Industry"):

        ui.h4("Number of Startups by Industry")
        @render_plotly
        def plot():
            industries = ["Built Environment", "Energy", "Environmental Services and Finance", 
                        "Materials & Manufacturing", "Nature and Agriculture", 
                        "Transportation", "Waste Management"]
            filt_df = df[df["Country"].isin(input.Country())]
            industry_count = filt_df['Industry'].value_counts()
            get_industry = {
                    'Industry': industries,
                    'Number of Startups': [industry_count.get(industry, 0) for industry in industries]
                }
            fig = px.treemap(
            get_industry,
                    path=['Industry'], 
                    values='Number of Startups',  
                    title="",
                )
            fig.update_layout(margin = dict(t=70, l=25, r=25, b=25))

            return fig
        
        @reactive.calc
        def fig():
            filt_df = df[df["Country"].isin(input.Country())]
            return filt_df 

    with ui.nav_panel("Investments"):

        ui.help_text("Due to the size of the graphs, this tab is best viewed on a computer/ large screen.")
        ui.p(" ")

        ui.h4("Time Horizon of Deal Volume and Deal Value")
        @render_plotly
        def flow():

            filt_df = df_additional[df_additional["Country"].str.lower().isin([country.lower() for country in input.Country()])]
            if filt_df.empty:
                raise ValueError("Please select the country/countries.")
            
            deal_count = filt_df["Period"].value_counts()
            stages = filt_df.groupby("Period").sum()
            
            print(stages.index)
            
            x = stages.index
            y_bar = deal_count.reindex(stages.index)
            y_area = stages["Funding Amount (Million USD)"]  

            area_trace = go.Scatter(
                x=x,
                y=y_area,
                fill="tozeroy",
                mode="lines+markers",
                name="Funding Amount (Million USD)",
                line=dict(color="lightsalmon"),
                yaxis="y1",  
            )
            
            bar_trace = go.Bar(
                x=x,
                y=y_bar,
                opacity=0.7,
                name="Number of Deals",
                marker=dict(color="lightgreen"),
                yaxis="y2",  
            )
            
            layout = go.Layout(
                yaxis=dict(
                    title="Funding Amount (USD)",
                    showgrid=False,
                ),
                yaxis2=dict(
                    title="Number of Deals",
                    overlaying="y",  
                    side="right",  
                ),
                xaxis=dict(
                    title="Period"
                ),
                legend=dict(
                    x=0,
                    y=1.2,
                    orientation="h"
                ),
            )
            
            deals = go.Figure(data=[area_trace, bar_trace], layout=layout)

            return deals

        ui.p(" ")

        ui.h4("Startups by Funding Stages")
        @render_plotly
        def fig():

            filt_df = df[df["Country"].isin(input.Country())]
            
            funding_stages = filt_df['Company Stage'].value_counts()
            custom_order = ["Undisclosed", "Funding Unknown", "Pre-Seed", "Seed", "Pre Series A", "Series A", "Series B", "Series C", "Series D", "Acquired"]
            funding_stages = funding_stages.reindex(custom_order, fill_value=0)

            scatter_trace = go.Scatter(
                x=funding_stages.index,
                y=funding_stages,
                mode='markers',
                marker=dict(
                    color='blue',
                    size=10,
                    line=dict(width=2, color='skyblue')
                ),
                name='Number of Startups'
            )

            vlines_trace = go.Bar(
                x=funding_stages.index,
                y=funding_stages,
                width=[0.05] * len(funding_stages),  
                marker=dict(
                    color='skyblue',
                    opacity=0.7
                ),
                name='Vertical Lines'
            )

            layout = go.Layout(
                title='',
                xaxis=dict(title='Funding Stage', tickangle=-45),
                yaxis=dict(title='Number of Startups'),
                showlegend=False
            )

            fig = go.Figure(data=[vlines_trace, scatter_trace], layout=layout)

            return fig

        ui.p(" ")

        ui.input_select(  
        "Stage",  
        "Select Funding Stage:",  
        {"Funding Unknown": "Funding Unknown", 
         "Undisclosed": "Undisclosed", 
         "Pre-Seed": "Pre-Seed",
         "Seed": "Seed",
         "Pre Series A": "Pre Series A",
         "Series A": "Series A",
         "Series B": "Series B",
         "Series C": "Series C",
         "Series D": "Series D",
         "Acquired": "Acquired",},  
        )

        with ui.value_box():
            "Startups by Funding Stage"
            @render.ui
            def get_funding_stage():
                
                df_filtered = filtered_df()
                stage_filtered_df = df_filtered[df_filtered['Company Stage'] == input.Stage()]
                company_stage_count = stage_filtered_df['Company Stage'].value_counts()
                return f"{input.Stage()}: {company_stage_count.get(input.Stage())}"
            
        @reactive.calc
        def filtered_df():
            filt_df = df[df["Country"].isin(input.Country())]
            return filt_df