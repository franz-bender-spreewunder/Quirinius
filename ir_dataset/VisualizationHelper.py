from matplotlib import pyplot as plt, animation


class VisualizationHelper:
    @staticmethod
    def sequence_to_video(sequence):
        frames = []
        fig = plt.figure(figsize=(3.2, 2.4))
        for img in sequence:
            frames.append([plt.imshow(img, animated=True)])

        ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True, repeat_delay=1000)
        plt.close()
        return ani.to_html5_video()

    @staticmethod
    def initialize_params():
        plt.rcParams['figure.figsize'] = [5, 5]
