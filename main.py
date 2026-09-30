from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView

from noaa_service import buscar_nino34
from inpe_service import buscar_focos_presidente_figueiredo, _classificar_risco
from ana_service import buscar_nivel_balbina
from inmet_service import buscar_dados_painel


def _classificar_cor_rapida(valor):
    if valor >= 2.0:
        return "Muito Forte", (0.72, 0.11, 0.11, 1)
    elif valor >= 1.5:
        return "Forte", (0.91, 0.30, 0.24, 1)
    elif valor >= 1.0:
        return "Moderado", (0.95, 0.61, 0.07, 1)
    elif valor >= 0.5:
        return "Fraco", (0.98, 0.80, 0.18, 1)
    elif valor > -0.5:
        return "Neutro", (0.13, 0.71, 0.43, 1)
    elif valor > -1.0:
        return "La Nina Fraco", (0.53, 0.85, 0.92, 1)
    elif valor > -1.5:
        return "La Nina Moderado", (0.13, 0.59, 0.95, 1)
    else:
        return "La Nina Forte", (0.10, 0.40, 0.78, 1)


class CardIndicador(MDCard):
    def __init__(self, titulo, valor, unidade, legenda, cor_valor, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self.padding = "12dp"
        self.spacing = "4dp"
        self.size_hint = (1, None)
        self.height = "130dp"

        self.add_widget(MDLabel(
            text=titulo,
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height="22dp",
        ))
        self.add_widget(MDLabel(
            text=valor + " " + unidade,
            halign="center",
            theme_text_color="Custom",
            text_color=cor_valor,
            font_style="H4",
            size_hint_y=None,
            height="52dp",
        ))
        self.add_widget(MDLabel(
            text=legenda,
            halign="center",
            theme_text_color="Hint",
            font_style="Caption",
            size_hint_y=None,
            height="22dp",
        ))


class TelaPainel(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView()
        layout = MDBoxLayout(
            orientation="vertical",
            padding="12dp",
            spacing="12dp",
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter("height"))

        layout.add_widget(MDLabel(
            text="[b]Presidente Figueiredo - AM[/b]",
            markup=True,
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height="42dp",
        ))
        layout.add_widget(MDLabel(
            text="Secretaria Municipal de Ordem Publica e Integracao  -  CICC",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body2",
            size_hint_y=None,
            height="26dp",
        ))
        layout.add_widget(MDLabel(
            text="Diretor do CICC - Inspetor 3a GALUCIO",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.13, 0.59, 0.95, 1),
            font_style="Body2",
            size_hint_y=None,
            height="26dp",
        ))

        dados = buscar_dados_painel()

        if dados.get("erro"):
            layout.add_widget(MDLabel(
                text="Nao foi possivel carregar os dados meteorologicos.",
                halign="center",
                theme_text_color="Error",
                font_style="Body1",
                size_hint_y=None,
                height="40dp",
            ))
        else:
            if dados.get("_do_cache"):
                texto_fonte = "SEM CONEXAO  |  " + dados["fonte"]
                cor_fonte = (0.95, 0.61, 0.07, 1)
            else:
                texto_fonte = "Atualizado em: " + dados["hora"] + "  |  Fonte: " + dados["fonte"]
                cor_fonte = (0.6, 0.6, 0.6, 1)

            layout.add_widget(MDLabel(
                text=texto_fonte,
                halign="center",
                theme_text_color="Custom",
                text_color=cor_fonte,
                font_style="Caption",
                size_hint_y=None,
                height="22dp",
            ))

            grid = MDGridLayout(cols=2, spacing="12dp", size_hint_y=None, height="290dp")

            grid.add_widget(CardIndicador(
                "TEMPERATURA", str(dados["temperatura"]), "C",
                "Dado real", dados["cor_temperatura"],
            ))
            grid.add_widget(CardIndicador(
                "UMIDADE", str(dados["umidade"]), "%",
                dados["texto_umidade"], dados["cor_umidade"],
            ))
            grid.add_widget(CardIndicador(
                "VENTO", str(dados["vento"]), "km/h",
                "Direcao: " + dados["direcao"], (0.13, 0.59, 0.95, 1),
            ))
            grid.add_widget(CardIndicador(
                "CHUVA (7 DIAS)", str(dados["chuva_7d"]), "mm",
                "Acumulado", (0.13, 0.59, 0.95, 1),
            ))

            layout.add_widget(grid)

        card_resumo = MDCard(
            orientation="vertical",
            padding="16dp",
            spacing="8dp",
            size_hint=(1, None),
            height="120dp",
        )
        card_resumo.add_widget(MDLabel(
            text="[b]Resumo do dia[/b]",
            markup=True,
            font_style="H6",
            size_hint_y=None,
            height="30dp",
        ))
        card_resumo.add_widget(MDLabel(
            text="Tempo quente e seco. Umidade abaixo do ideal, risco de incendio elevado no entorno.",
            theme_text_color="Secondary",
        ))
        layout.add_widget(card_resumo)

        scroll.add_widget(layout)
        self.add_widget(scroll)


class TelaSeca(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView()
        layout = MDBoxLayout(
            orientation="vertical",
            padding="16dp",
            spacing="14dp",
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter("height"))

        layout.add_widget(MDLabel(
            text="[b]Seca Amazonica[/b]",
            markup=True,
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height="50dp",
        ))
        layout.add_widget(MDLabel(
            text="Presidente Figueiredo - AM",
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height="22dp",
        ))

        dados = buscar_nivel_balbina()

        card_nivel = MDCard(
            orientation="vertical",
            padding="20dp",
            spacing="8dp",
            size_hint=(1, None),
            height="230dp",
        )
        card_nivel.add_widget(MDLabel(
            text="NIVEL DO RIO UATUMA",
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height="24dp",
        ))
        card_nivel.add_widget(MDLabel(
            text="Estacao " + dados["estacao"],
            halign="center",
            theme_text_color="Hint",
            font_style="Caption",
            size_hint_y=None,
            height="22dp",
        ))
        card_nivel.add_widget(MDLabel(
            text=str(dados["nivel_m"]) + " m",
            halign="center",
            theme_text_color="Custom",
            text_color=dados["cor"],
            font_style="H2",
            size_hint_y=None,
            height="90dp",
        ))
        card_nivel.add_widget(MDLabel(
            text="[b]" + dados["classificacao"] + "[/b]",
            markup=True,
            halign="center",
            theme_text_color="Custom",
            text_color=dados["cor"],
            font_style="H6",
            size_hint_y=None,
            height="36dp",
        ))
        card_nivel.add_widget(MDLabel(
            text="Referencia: " + dados["data"] + " " + dados["hora"],
            halign="center",
            theme_text_color="Hint",
            font_style="Caption",
            size_hint_y=None,
            height="24dp",
        ))
        layout.add_widget(card_nivel)

        card_info = MDCard(
            orientation="vertical",
            padding="16dp",
            spacing="6dp",
            size_hint=(1, None),
            height="180dp",
        )
        card_info.add_widget(MDLabel(
            text="[b]Caracteristicas do Rio[/b]",
            markup=True,
            halign="center",
            font_style="H6",
            size_hint_y=None,
            height="32dp",
        ))
        card_info.add_widget(MDLabel(
            text="Amplitude historica: " + str(dados["amplitude"]) + " m",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height="30dp",
        ))
        card_info.add_widget(MDLabel(
            text="Pico de cheia: " + dados["pico_cheia"],
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height="30dp",
        ))
        card_info.add_widget(MDLabel(
            text="Pico de seca: " + dados["pico_seca"],
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1",
            size_hint_y=None,
            height="30dp",
        ))
        layout.add_widget(card_info)

        if dados.get("nota"):
            layout.add_widget(MDLabel(
                text=dados["nota"],
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
                size_hint_y=None,
                height="40dp",
            ))

        layout.add_widget(MDLabel(
            text="Fonte: ANA - HidroWebService (Estacao 16080000)",
            halign="center",
            theme_text_color="Hint",
            font_style="Caption",
            size_hint_y=None,
            height="24dp",
        ))

        scroll.add_widget(layout)
        self.add_widget(scroll)


class TelaIncendio(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView()
        layout = MDBoxLayout(
            orientation="vertical",
            padding="16dp",
            spacing="14dp",
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter("height"))

        layout.add_widget(MDLabel(
            text="[b]Risco de Incendio[/b]",
            markup=True,
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height="50dp",
        ))
        layout.add_widget(MDLabel(
            text="Presidente Figueiredo - AM  |  Ultimos 7 dias",
            halign="center",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height="22dp",
        ))

        dados = buscar_focos_presidente_figueiredo()

        if dados["erro"]:
            card_erro = MDCard(
                orientation="vertical",
                padding="20dp",
                spacing="10dp",
                size_hint=(1, None),
                height="150dp",
            )
            card_erro.add_widget(MDLabel(
                text="Nao foi possivel carregar os dados do INPE.",
                halign="center",
                theme_text_color="Error",
                font_style="H6",
                size_hint_y=None,
                height="36dp",
            ))
            card_erro.add_widget(MDLabel(
                text=dados["erro"],
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
            ))
            layout.add_widget(card_erro)

        else:
            card_total = MDCard(
                orientation="vertical",
                padding="20dp",
                spacing="8dp",
                size_hint=(1, None),
                height="190dp",
            )
            card_total.add_widget(MDLabel(
                text="FOCOS DETECTADOS",
                halign="center",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))

            if dados["total"] > 0:
                cor_total = (0.91, 0.30, 0.24, 1)
            else:
                cor_total = (0.13, 0.71, 0.43, 1)

            card_total.add_widget(MDLabel(
                text=str(dados["total"]),
                halign="center",
                theme_text_color="Custom",
                text_color=cor_total,
                font_style="H1",
                size_hint_y=None,
                height="90dp",
            ))

            subtexto = str(dados["dias_com_foco"]) + " dia(s) com foco"
            card_total.add_widget(MDLabel(
                text=subtexto,
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))
            layout.add_widget(card_total)

            if dados["total"] > 0:
                texto_risco, cor_risco = _classificar_risco(dados["risco_max"])
                card_risco = MDCard(
                    orientation="vertical",
                    padding="16dp",
                    spacing="6dp",
                    size_hint=(1, None),
                    height="110dp",
                )
                card_risco.add_widget(MDLabel(
                    text="RISCO MAXIMO DETECTADO",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Caption",
                    size_hint_y=None,
                    height="22dp",
                ))
                card_risco.add_widget(MDLabel(
                    text="[b]" + texto_risco + "[/b]",
                    markup=True,
                    halign="center",
                    theme_text_color="Custom",
                    text_color=cor_risco,
                    font_style="H4",
                    size_hint_y=None,
                    height="52dp",
                ))
                card_risco.add_widget(MDLabel(
                    text="FRP maximo: " + str(round(dados["frp_max"], 1)) + " MW",
                    halign="center",
                    theme_text_color="Hint",
                    font_style="Caption",
                    size_hint_y=None,
                    height="22dp",
                ))
                layout.add_widget(card_risco)

                altura_card = 70 + len(dados["por_dia"]) * 32
                card_dias = MDCard(
                    orientation="vertical",
                    padding="16dp",
                    spacing="6dp",
                    size_hint=(1, None),
                    height=str(altura_card) + "dp",
                )
                card_dias.add_widget(MDLabel(
                    text="[b]Distribuicao por dia[/b]",
                    markup=True,
                    halign="center",
                    font_style="H6",
                    size_hint_y=None,
                    height="34dp",
                ))

                for dia in sorted(dados["por_dia"].keys(), reverse=True):
                    qtd = dados["por_dia"][dia]
                    if qtd >= 10:
                        cor_dia = (0.72, 0.11, 0.11, 1)
                    elif qtd >= 5:
                        cor_dia = (0.91, 0.30, 0.24, 1)
                    elif qtd >= 1:
                        cor_dia = (0.95, 0.61, 0.07, 1)
                    else:
                        cor_dia = (0.13, 0.71, 0.43, 1)

                    card_dias.add_widget(MDLabel(
                        text=dia + "     " + str(qtd) + " foco(s)",
                        halign="center",
                        theme_text_color="Custom",
                        text_color=cor_dia,
                        font_style="Body1",
                        size_hint_y=None,
                        height="32dp",
                    ))
                layout.add_widget(card_dias)

            else:
                card_limpo = MDCard(
                    orientation="vertical",
                    padding="20dp",
                    spacing="8dp",
                    size_hint=(1, None),
                    height="110dp",
                )
                card_limpo.add_widget(MDLabel(
                    text="Nenhum foco detectado",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.13, 0.71, 0.43, 1),
                    font_style="H6",
                    size_hint_y=None,
                    height="40dp",
                ))
                card_limpo.add_widget(MDLabel(
                    text="Sem focos em Presidente Figueiredo nos ultimos 7 dias.",
                    halign="center",
                    theme_text_color="Hint",
                    font_style="Caption",
                ))
                layout.add_widget(card_limpo)

            texto_fonte_inc = "Fonte: INPE - Programa Queimadas"
            cor_fonte_inc = (0.6, 0.6, 0.6, 1)
            if dados.get("_do_cache"):
                texto_fonte_inc = "SEM CONEXAO  |  " + dados["fonte"]
                cor_fonte_inc = (0.95, 0.61, 0.07, 1)

            layout.add_widget(MDLabel(
                text=texto_fonte_inc,
                halign="center",
                theme_text_color="Custom",
                text_color=cor_fonte_inc,
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))

        scroll.add_widget(layout)
        self.add_widget(scroll)


class TelaENSO(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView()
        layout = MDBoxLayout(
            orientation="vertical",
            padding="16dp",
            spacing="14dp",
            size_hint_y=None,
        )
        layout.bind(minimum_height=layout.setter("height"))

        layout.add_widget(MDLabel(
            text="[b]Status do El Nino[/b]",
            markup=True,
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height="50dp",
        ))

        dados = buscar_nino34()

        if dados["erro"]:
            card_erro = MDCard(
                orientation="vertical",
                padding="20dp",
                spacing="10dp",
                size_hint=(1, None),
                height="150dp",
            )
            card_erro.add_widget(MDLabel(
                text="Nao foi possivel carregar os dados do NOAA.",
                halign="center",
                theme_text_color="Error",
                font_style="H6",
                size_hint_y=None,
                height="36dp",
            ))
            card_erro.add_widget(MDLabel(
                text=dados["erro"],
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
            ))
            layout.add_widget(card_erro)
        else:
            card = MDCard(
                orientation="vertical",
                padding="20dp",
                spacing="8dp",
                size_hint=(1, None),
                height="240dp",
            )
            card.add_widget(MDLabel(
                text="INDICE NINO 3.4",
                halign="center",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))
            sinal = "+" if dados["valor"] >= 0 else ""
            card.add_widget(MDLabel(
                text=sinal + str(dados["valor"]) + " C",
                halign="center",
                theme_text_color="Custom",
                text_color=dados["cor"],
                font_style="H3",
                size_hint_y=None,
                height="70dp",
            ))
            card.add_widget(MDLabel(
                text="[b]" + dados["classificacao"] + "[/b]",
                markup=True,
                halign="center",
                theme_text_color="Custom",
                text_color=dados["cor"],
                font_style="H6",
                size_hint_y=None,
                height="36dp",
            ))
            card.add_widget(MDLabel(
                text="Referencia: " + str(dados["mes"]) + "/" + str(dados["ano"]),
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))
            layout.add_widget(card)

            card_tend = MDCard(
                orientation="vertical",
                padding="16dp",
                spacing="6dp",
                size_hint=(1, None),
                height="100dp",
            )
            card_tend.add_widget(MDLabel(
                text="TENDENCIA",
                halign="center",
                theme_text_color="Secondary",
                font_style="Caption",
                size_hint_y=None,
                height="22dp",
            ))
            card_tend.add_widget(MDLabel(
                text="[b]" + dados["tendencia"] + "[/b]",
                markup=True,
                halign="center",
                theme_text_color="Custom",
                text_color=dados["cor_tendencia"],
                font_style="H5",
                size_hint_y=None,
                height="40dp",
            ))
            sinal_var = "+" if dados["variacao"] >= 0 else ""
            card_tend.add_widget(MDLabel(
                text="Variacao mensal: " + sinal_var + str(dados["variacao"]) + " C",
                halign="center",
                theme_text_color="Hint",
                font_style="Caption",
                size_hint_y=None,
                height="22dp",
            ))
            layout.add_widget(card_tend)

            card_hist = MDCard(
                orientation="vertical",
                padding="16dp",
                spacing="6dp",
                size_hint=(1, None),
                height="270dp",
            )
            card_hist.add_widget(MDLabel(
                text="[b]Ultimos 6 meses[/b]",
                markup=True,
                halign="center",
                font_style="H6",
                size_hint_y=None,
                height="32dp",
            ))
            for item in reversed(dados["historico"]):
                _, cor_item = _classificar_cor_rapida(item["valor"])
                sinal_item = "+" if item["valor"] >= 0 else ""
                texto = str(item["mes"]).zfill(2) + "/" + str(item["ano"]) + "   " + sinal_item + str(item["valor"]) + " C"
                card_hist.add_widget(MDLabel(
                    text=texto,
                    halign="center",
                    theme_text_color="Custom",
                    text_color=cor_item,
                    font_style="Body1",
                    size_hint_y=None,
                    height="30dp",
                ))
            layout.add_widget(card_hist)

            texto_fonte_enso = "Fonte: NOAA CPC - detrend.nino34.ascii.txt"
            cor_fonte_enso = (0.6, 0.6, 0.6, 1)
            if dados.get("_do_cache"):
                texto_fonte_enso = "SEM CONEXAO  |  " + dados["fonte"]
                cor_fonte_enso = (0.95, 0.61, 0.07, 1)

            layout.add_widget(MDLabel(
                text=texto_fonte_enso,
                halign="center",
                theme_text_color="Custom",
                text_color=cor_fonte_enso,
                font_style="Caption",
                size_hint_y=None,
                height="24dp",
            ))

        scroll.add_widget(layout)
        self.add_widget(scroll)


class CICCPFElNinoApp(MDApp):
    def build(self):
        self.title = "CICC PF - El Nino"
        self.theme_cls.primary_palette = "BlueGray"
        self.theme_cls.theme_style = "Dark"

        nav = MDBottomNavigation()

        item_painel = MDBottomNavigationItem(name="painel", text="Painel", icon="view-dashboard")
        item_painel.add_widget(TelaPainel())
        nav.add_widget(item_painel)

        item_seca = MDBottomNavigationItem(name="seca", text="Seca", icon="water-off")
        item_seca.add_widget(TelaSeca())
        nav.add_widget(item_seca)

        item_incendio = MDBottomNavigationItem(name="incendio", text="Incendio", icon="fire")
        item_incendio.add_widget(TelaIncendio())
        nav.add_widget(item_incendio)

        item_enso = MDBottomNavigationItem(name="enso", text="ENSO", icon="earth")
        item_enso.add_widget(TelaENSO())
        nav.add_widget(item_enso)

        return nav


if __name__ == "__main__":
    CICCPFElNinoApp().run()
