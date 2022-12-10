import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
import os

galaxies = ["elliptical", "S0", "Sa", "Sb", "sbt1", "sbt2", "sbt3", "sbt4", "sbt5", "sbt6", "galaxy"]
colors = ["b", "g", "r", "c", "m", "y", "k"]
shapes = ['.', ',', 'o', 'v', '^', '<', '>', '1', '2', '3', '4', '8', 's', 'p', 'P', '*', 'h',
          'H', '+', 'X', 'D', 'd', '|']


def save_new_fig_b_v(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name)
    morphology = ["sbt1" if "sbt" in galaxy else "S0" for galaxy in df["type"]]
    for i in ["lines", "points"]:
        draw_save_points(title="sbt or not rest frame b-i", xlabel="z", ylabel="rest log(b/i)", x=df["z"], y=df["rest log(b/i)"],
                         yerr=df["rest log(b/i)_err"], morphology=morphology, folder="../graphs/rest B-V",
                         file_name=f"sbt or not rest B-I_{i}", lines=i=="lines")

def save_figs_b_v(path, sheet_name):
    filters = ["b", "i", "u", "v"]
    df = pd.read_excel(path, sheet_name=sheet_name)
    for i, light_filter in enumerate(filters):
        for other in filters[i+1:]:
            cul = f"log({light_filter}/{other})"
            draw_save_points(title=f"{cul} to z", xlabel="z", ylabel=cul, x=df["z"], y=df[cul], yerr=df[f"{cul}_err"],
                             morphology=df["type"])


def get_data_and_draw(path, sheet_name, title, xlabel, ylabel, x, y, yerr):
    df = pd.read_excel(path, sheet_name=sheet_name)
    # if i use this i need to fix this one, not best practice
    draw_save_points(title, xlabel, ylabel, df[x], df[y], df[yerr], df["type"], folder="", file_name="")


def draw_save_points(title, xlabel, ylabel, x, y, yerr, morphology, folder, file_name, lines):
    galaxies_colors = make_color_dict()
    data_by_galaxy = {}
    for x_point, y_point, yerr_point, galaxy in zip(x, y, yerr, morphology):
            if galaxy in data_by_galaxy.keys():
                data_by_galaxy[galaxy]["x"].append(x_point)
                data_by_galaxy[galaxy]["y"].append(y_point)
                data_by_galaxy[galaxy]["yerr"].append(yerr_point)
            else:
                data_by_galaxy[galaxy] = {
                    "x": [x_point],
                    "y": [y_point],
                    "yerr": [yerr_point]
                }

    for galaxy, data in data_by_galaxy.items():
        sorted_data = sorted([(x, y, yerr) for x, y, yerr in zip(data["x"], data["y"], data["yerr"])], key=lambda x: x[0])
        x = [point[0] for point in sorted_data]
        y = [point[1] for point in sorted_data]
        yerr = [point[2] for point in sorted_data]
        plt.errorbar(x, y, yerr, fmt=galaxies_colors[galaxy], label=galaxy)
        if lines:
            plt.plot(x, y, galaxies_colors[galaxy][1])

    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.grid()
    plt.legend()
    # plt.show()
    # plt.savefig("../graphs/flux_x-flux_y/" + f"{ylabel}"[4:7].replace("/", "-"))
    plt.savefig(os.path.join(folder, file_name))
    plt.clf()

def make_color_dict():
    return {galaxy: f"{random.choice(shapes)}{random.choice(colors)}" for galaxy in galaxies}




if __name__ == '__main__':
    # save_figs_b_v(r"C:\Users\User\OneDrive - mail.tau.ac.il\Lab 1\מעבדה ב\סמסטר א\אסטרו\galaxies.xlsx", sheet_name="summary")
    save_new_fig_b_v("../summary analyze.xlsx", "restframedata")