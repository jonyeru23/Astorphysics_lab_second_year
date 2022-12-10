from SFR import *
from B_V_redshift import *


def get_accumulative_graph(data_path, sheet_name, folder):
    """i assume the df is sorted by z"""
    df = pd.read_excel(data_path, sheet_name=sheet_name)
    z = df["z"]
    SFRD, SFRD_err = clean(*get_SFRD(df))
    SFRD, SFRD_err = np.array(SFRD), np.array(SFRD_err)
    morphology = ["galaxy" for i in df["type"]]
    for i in ["lines", "points"]:
        draw_save_points(title="log(SFRD) to z", xlabel="z", ylabel="log(SFRD) [sollMass / year / Mpc^3]",
                         x=z, y=np.log10(SFRD), yerr=np.log(10)*SFRD_err/SFRD, morphology=morphology, folder=folder,
                         file_name=f"SFRD to z_{i} natural", lines=i=="lines")


def get_Luminosity_graphs(data_path, sheet_name, folder):
    df = pd.read_excel(data_path, sheet_name=sheet_name)
    x = df["z"]
    morphology = ["sbt1" if "sbt" in galaxy else "S0" for galaxy in df["type"]]
    for band in ["b", "u", "i", "v"]:
        y, yerr = clean(*get_L_lambda(df, band))
        y, yerr = np.array(y), np.array(yerr)

    ## insert changes here
        for word in ["lines", "points"]:
            draw_save_points(title=f"sbt or not log(Luminosity_{band}) to z", xlabel="z",
                             ylabel=f"log(Luminosity_{band})[erg / s / A]",
                             x=x, y=np.log10(y), yerr=np.log(10)*yerr/y, morphology=morphology, folder=folder,
                             file_name=f"sbt or not log(Luminosity_{band}_{word})",
                     lines=word == "lines")

def get_cov(data_path, sheet_name):
    df = pd.read_excel(data_path, sheet_name=sheet_name)
    x = df["z"]
    morphology = ["sbt1" if "sbt" in galaxy else "S0" for galaxy in df["type"]]
    for morph in ["sbt1", "S0"]:
        for band in ["b", "v"]:
            y, yerr = clean(*get_L_lambda(df, band))
            y, yerr = np.array(y), np.array(yerr)
            sbt1_x, sbt1_y = [x[i] for i in range(len(x)) if morphology[i] == morph], [y[i] for i in range(len(x)) if
                                                                                        morphology[i] == morph]
            print(f"{morph} {band} cov:  {np.corrcoef(np.array(sbt1_x), np.array(sbt1_y))[1][0]}")

def get_SFR_graphs(path, sheet_name, folder):
    df = pd.read_excel(path, sheet_name=sheet_name)
    # x = [float(time.to(u.year).value) for time in back_in_time(np.array(df["z"]))]
    morphology = ["sbt1" if "sbt" in galaxy else "S0" for galaxy in df["type"]]
    x = df["z"]
    y, yerr = clean(*get_SFR(df))
    x, y, yerr = clear_nones(x, y, yerr)
    for word in ["lines", "points"]:
        draw_save_points(title="sbt or not SFR to z", xlabel="z", ylabel="SFR[solMass/year]",
                         x=x, y=y, yerr=yerr, morphology=morphology, folder=folder, file_name=f"sbt or not SFR to z_{word}",
                         lines=word == "lines")


def clear_nones(x, y, yerr):
    assert len(x) == len(y) == len(yerr)
    i = 0
    while i < len(x):
        if y[i] == yerr[i] == 0:
            x.pop(i)
            y.pop(i)
            yerr.pop(i)
            i -= 1
        i += 1
    return x, y, yerr



def get_L_lambda(df, band):
    """
    getting the Luminosity_lambda
    """
    z = np.array(df["z"])
    flux = get_flux(df)
    return L_lambda(z, flux[band]["value"]), L_lambda_err(z, flux_lambda=flux[band]["value"],
                                                                flux_lambda_err=flux[band]["error"])



if __name__ == '__main__':
    # get_Luminosity_graphs("../summary analyze.xlsx", sheet_name="data", folder="../graphs/luminosity_log_scale")
    # get_SFR_graphs("../summary analyze.xlsx", sheet_name="data", folder="../graphs/SFR to z")
    get_accumulative_graph("../summary analyze.xlsx", sheet_name="data", folder="../graphs/SFRD")
    # get_cov("../summary analyze.xlsx", sheet_name="data")