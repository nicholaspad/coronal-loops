    @toggle_pylab
    def raw_img(self, K, PATH, dpi, **matplot_args):
        figure = plt.figure(frameon=False)
        axes = plt.Axes(figure, [0., 0., 1., 1.])
        axes.set_axis_off()
        figure.add_axes(axes)
        matplot_args.update({'annotate': False, "_basic_plot": True})
        im = self.plot(axes=axes, **matplot_args)
        file = "/Users/padman/Desktop/lmsal/%s/raw_%04d" % (PATH, K)
        figure.savefig(file, dpi = dpi)
        temp = Image.open(file + ".png")
        temp = temp.crop((200,0,1400,1200))
        temp.save(file + ".png")
        plt.close()
        return None

    @toggle_pylab
    def e_img(self, K, PATH, dpi, **matplot_args):
        figure = plt.figure(frameon=False)
        axes = plt.Axes(figure, [0., 0., 1., 1.])
        axes.set_axis_off()
        figure.add_axes(axes)
        matplot_args.update({'annotate': False, "_basic_plot": True})
        im = self.plot(axes=axes, **matplot_args)
        file = "/Users/padman/Desktop/lmsal/%s/enhanced_%04d" % (PATH, K)
        figure.savefig(file, dpi = dpi)
        temp = Image.open(file + ".png")
        temp = temp.crop((200,0,1400,1200))
        temp.save(file + ".png")
        plt.close()
        return None