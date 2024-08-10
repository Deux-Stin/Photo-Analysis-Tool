class PlotManager:
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        
    def plot_by_date(self, photos):
        dates = [p['date_taken'].date() for p in photos if p['date_taken'] != 'Unknown']
        unique_dates, counts = np.unique(dates, return_counts=True)
        self.plot_widget.clear()
        self.plot_widget.plot(unique_dates, counts, stepMode=True, fillLevel=0, brush='r')

    def plot_by_hour(self, photos):
        hours = [int(p['hour_taken'].split(':')[0]) for p in photos if p['hour_taken'] != 'Unknown']
        counts, bins = np.histogram(hours, bins=24, range=(0, 24))
        bins = np.append(bins, bins[-1] + 1)
        self.plot_widget.clear()
        self.plot_widget.plot(bins, np.append(counts, counts[-1]), stepMode=True, fillLevel=0, brush='g')
