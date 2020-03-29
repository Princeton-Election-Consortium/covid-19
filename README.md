Purpose: dynamically generate COVID-19 plots for PEC website

Python version: 3x

Dependencies: numpy, pandas, matplotlib, seaborn

Overall workflow:
* cron job runs run.sh daily
* run.sh calls main.py to produce plots
* main.py scrapes JHU data, calculates relevant metrics, and generates plots


Detailed description:
The bulk of the workflow is controlled by main.py, which starts by reading in the latest JHU data and ends by saving out image files to the `images` directory. Within this flow, there are 3 main steps:

* scraping: the scrape.py module reads the daily data files from JHU repository and extracts the relevant metric (e.g. deaths or confirmed cases) for a select set of regions of interest (all listed at the top of scrape.py). The `scrape_regional_data` function allows for scraping of specific regions and variables, whereas the `scrape_all_regions` function collects the desired data in bulk (all regions specified at the top of the module). The data are saved in a single pandas DataFrame which is saved as a csv in the `data` directory. Columns correspond to regions (e.g. US or New Jersey) and rows to days. As an example, a single cell may correspond to "the number of deaths on March 25 in New Jersey."

* calculations: the `calculations.calculate` function reads in the scraped data file described above and performs specific calculations (e.g. compute doubling time). The results are saved as a single pandas DataFrame which is saved as a csv in the `data` directory. Columns correspond to regions and rows correspond to days. As an example, a single cell may correspond to "the estimated doubling time on March 25 in New Jersey."

* plotting: the `displays.generate_plot` function reads in the calculated values from the above step and produces a single plot. It accepts a list of columns (i.e. regions) to include as individual data lines in the plot. It also accepts a number of parameters to control the formatting of the plot. In addition, an extended list of parameters controlling the specifics of the plot formatting is at the top of the `displays` module. The plots are saved as images to the `images` directory, and they are named according to the parameters used to generate the data.
