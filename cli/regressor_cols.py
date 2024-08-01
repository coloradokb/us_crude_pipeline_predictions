def all_cols():
    full_list = [
        "TOTALSUPPLY", "WCRSTUS1", "WCESTUS1", "WCESTP11", "WCESTP21", "W_EPC0_SAX_YCUOK_MBBL",
        "WCESTP31", "WCESTP41", "WCESTP51", "W_EPC0_SKA_NUS_MBBL", "WCSSTUS1", "WGTSTUS1",
        "WGTSTP11", "WGTSTP21", "WGTSTP31", "WGTSTP41", "WGTSTP51", "WGFSTUS1", "WGRSTUS1",
        "WGRSTP11", "WGRSTP21", "WGRSTP31", "WGRSTP41", "WGRSTP51", "WG1ST_NUS_1", "WG1ST_R10_1",
        "WG1ST_R20_1", "WG1ST_R30_1", "WG1ST_R40_1", "WG1ST_R50_1", "WG3ST_NUS_1", "WG3ST_R10_1",
        "WG3ST_R20_1", "WG3ST_R30_1", "WG3ST_R40_1", "WG3ST_R50_1", "WG4ST_NUS_1", "WG4ST_R10_1",
        "WG4ST_R20_1", "WG4ST_R30_1", "WG4ST_R40_1", "WG4ST_R50_1", "WG5ST_NUS_1", "WG5ST_R10_1",
        "WG5ST_R20_1", "WG5ST_R30_1", "WG5ST_R40_1", "WG5ST_R50_1", "W_EPM0CAL55_SAE_NUS_MBBL",
        "W_EPM0CAL55_SAE_R10_MBBL", "W_EPM0CAL55_SAE_R20_MBBL", "W_EPM0CAL55_SAE_R30_MBBL",
        "W_EPM0CAL55_SAE_R40_MBBL", "W_EPM0CAL55_SAE_R50_MBBL", "W_EPM0CAG55_SAE_NUS_MBBL",
        "W_EPM0CAG55_SAE_R10_MBBL", "W_EPM0CAG55_SAE_R20_MBBL", "W_EPM0CAG55_SAE_R30_MBBL",
        "W_EPM0CAG55_SAE_R40_MBBL", "W_EPM0CAG55_SAE_R50_MBBL", "WG6ST_NUS_1", "WG6ST_R10_1",
        "WG6ST_R20_1", "WG6ST_R30_1", "WG6ST_R40_1", "WG6ST_R50_1", "WBCSTUS1", "WBCST_R10_1",
        "WBCST_R20_1", "WBCST_R30_1", "WBCST_R40_1", "WBCST_R50_1", "W_EPOBGRR_SAE_NUS_MBBL",
        "W_EPOBGRR_SAE_R10_MBBL", "W_EPOBGRR_SAE_R20_MBBL", "W_EPOBGRR_SAE_R30_MBBL",
        "W_EPOBGRR_SAE_R40_MBBL", "W_EPOBGRR_SAE_R50_MBBL", "WO6ST_NUS_1", "WO6ST_R10_1",
        "WO6ST_R20_1", "WO6ST_R30_1", "WO6ST_R40_1", "WO6ST_R50_1", "WO7ST_NUS_1", "WO7ST_R10_1",
        "WO7ST_R20_1", "WO7ST_R30_1", "WO7ST_R40_1", "WO7ST_R50_1", "WO9ST_NUS_1", "WO9ST_R10_1",
        "WO9ST_R20_1", "WO9ST_R30_1", "WO9ST_R40_1", "WO9ST_R50_1", "W_EPOOXE_SAE_NUS_MBBL",
        "W_EPOOXE_SAE_R10_MBBL", "W_EPOOXE_SAE_R20_MBBL", "W_EPOOXE_SAE_R30_MBBL",
        "W_EPOOXE_SAE_R40_MBBL", "W_EPOOXE_SAE_R50_MBBL", "WKJSTUS1", "WKJSTP11", "WKJSTP21",
        "WKJSTP31", "WKJSTP41", "WKJSTP51", "WDISTUS1", "WDISTP11", "WDIST1A1", "WDIST1B1",
        "WDIST1C1", "WDISTP21", "WDISTP31", "WDISTP41", "WDISTP51", "WD0ST_NUS_1", "WD0ST_R10_1",
        "WD0ST_R1X_1", "WD0ST_R1Y_1", "WD0ST_R1Z_1", "WD0ST_R20_1", "WD0ST_R30_1", "WD0ST_R40_1",
        "WD0ST_R50_1", "WD1ST_NUS_1", "WD1ST_R10_1", "WD1ST_R1X_1", "WD1ST_R1Y_1", "WD1ST_R1Z_1",
        "WD1ST_R20_1", "WD1ST_R30_1", "WD1ST_R40_1", "WD1ST_R50_1", "WDGSTUS1", "WDGSTP11",
        "WDGST1A1", "WDGST1B1", "WDGST1C1", "WDGSTP21", "WDGSTP31", "WDGSTP41", "WDGSTP51",
        "WRESTUS1", "WRESTP11", "WREST1A1", "WREST1B1", "WREST1C1", "WRESTP21", "WRESTP31",
        "WRESTP41", "WRESTP51", "WPRSTUS1", "WPRSTP11", "WPRST1A1", "WPRST1B1", "WPRST1C1",
        "WPRSTP21", "WPRSTP31", "WPRST_R4N5_1", "W_EPLLP0C_SKB_NUS_MBBL", "WPLSTUS1",
        "W_EPPO6_SAE_NUS_MBBL", "WUOSTUS1", "W_EPPK_SAE_NUS_MBBL", "W_EPPA_SAE_NUS_MBBL",
        "W_EPL0XP_SAE_NUS_MBBL", "WTESTUS1", "WTTSTUS1", "W_EPLLP0C_SKB_R10_MBBL",
        "W_EPLLP0C_SKB_R1X_MBBL", "W_EPLLP0C_SKB_R1Y_MBBL", "W_EPLLP0C_SKB_R1Z_MBBL",
        "W_EPLLP0C_SKB_R20_MBBL", "W_EPLLP0C_SKB_R30_MBBL", "W_EPLLP0C_SKB_R40_MBBL",
        "W_EPLLP0C_SKB_R50_MBBL", "CurrentClose", "FuturesClose"
    ]
    return full_list


def cols_for_total():
    """
    When predicting all/total of pipeline flow amounts, we only want regressor columns that
    are not part of the total (sum) of all pads. Otherwise, we would essentially be learning
    a relationship that is already defined by basic math
    """
    full_list = ["CurrentClose", "FuturesClose"]
    return full_list


def feature_selection():
    full_list = [
        "TOTALSUPPLY", "WCRSTUS1", "WCESTUS1", "WCESTP11", "WCESTP21", "W_EPC0_SAX_YCUOK_MBBL",
        "WCESTP31", "WCESTP41", "WCESTP51", "W_EPC0_SKA_NUS_MBBL", "WCSSTUS1", "WGTSTUS1",
        "WGTSTP11", "WGTSTP21", "WGTSTP31", "WGTSTP41", "WGTSTP51", "WGFSTUS1",
        "CurrentClose", "FuturesClose"
    ]

    return full_list


def future_regressors():
    full_list = ["CurrentClose", "FuturesClose"]

    return full_list
