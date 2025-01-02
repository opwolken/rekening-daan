function getJSONData(id) {
    const el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : null;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR' }).format(value);
}

function getCSSVariableValue(variable) {
    return getComputedStyle(document.documentElement).getPropertyValue(variable).trim();
}

const accentColor = getCSSVariableValue('--accent');
const redColor = getCSSVariableValue('--red');
const orangeColor = getCSSVariableValue('--orange');
const blueColor = getCSSVariableValue('--blue');
const purpleColor = getCSSVariableValue('--purple');

function generateColorVariants(baseColor, count) {
    const colorVariants = [];
    const color = baseColor.match(/\d+/g).map(Number);
    for (let i = 0; i < count; i++) {
        const factor = 1 - (i / count) * 0.5;
        colorVariants.push(`rgba(${color[0] * factor}, ${color[1] * factor}, ${color[2] * factor}, 0.6)`);
    }
    return colorVariants;
}

const baseColors = [accentColor, redColor, orangeColor, blueColor, purpleColor];
const colorVariants = baseColors.flatMap(color => generateColorVariants(color, 5));

// 1. Uren-van-de-dag (bar chart)
const urenLabels = getJSONData("urenLabels");
const urenData = getJSONData("urenData");
const ctxUren = document.getElementById("urenChart").getContext("2d");
new Chart(ctxUren, {
    type: "bar",
    data: {
        labels: urenLabels,
        datasets: [{
            label: "Uitgaven per uur",
            data: urenData,
            backgroundColor: accentColor
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { ticks: { color: "#f4f4f4" } },
            y: { ticks: { color: "#f4f4f4" } }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return formatCurrency(tooltipItem.raw);
                    }
                }
            }
        }
    }
});

// 2. Spaartrend (line chart)
const spaartrendLabels = getJSONData("spaartrendLabels");
const spaartrendData = getJSONData("spaartrendData");
const spaartrendAvgData = getJSONData("spaartrendAvgData");
const ctxSpaar = document.getElementById("spaartrendChart").getContext("2d");
new Chart(ctxSpaar, {
    type: "line",
    data: {
        labels: spaartrendLabels,
        datasets: [{
            label: "Cumulatief Sparen",
            data: spaartrendData,
            borderColor: accentColor,
            backgroundColor: "rgba(52,199,89,0.2)",
            fill: true,
            tension: 0.1
        }, {
            label: "3-maands Gemiddelde",
            data: spaartrendAvgData,
            borderColor: redColor,
            backgroundColor: "rgba(255,45,85,0.2)",
            fill: true,
            tension: 0.1
        }]
    },
    options: {
        responsive: true,
        scales: {
            x: { ticks: { color: "#f4f4f4" } },
            y: { ticks: { color: "#f4f4f4" } }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return formatCurrency(tooltipItem.raw);
                    }
                }
            }
        }
    }
});

// 3. Inkomentrend (stacked bar chart + 12-maanden gemiddelde)
let isYearly = false;
const inkomenLabels = getJSONData("inkomenLabels");
const inkomenDatasets = getJSONData("inkomenDatasets");
const inkomenAvgData = getJSONData("inkomenAvgData");
const ctxInkomen = document.getElementById("inkomenChart").getContext("2d");
const inkomenChart = new Chart(ctxInkomen, {
    type: "bar",
    data: {
        labels: inkomenLabels,
        datasets: [
            ...inkomenDatasets,
            {
                label: "12-maanden Gemiddelde",
                data: inkomenAvgData,
                type: "line",
                borderColor: redColor,
                backgroundColor: "rgba(255,45,85,0.2)",
                fill: false,
                tension: 0.1
            }
        ]
    },
    options: {
        responsive: true,
        scales: {
            x: { ticks: { color: "#f4f4f4" },
                 stacked: true 
            },
            y: { 
                ticks: { color: "#f4f4f4" },
                stacked: true
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return formatCurrency(tooltipItem.raw);
                    },
                    footer: (tooltipItems) => {
                        const totalAllDatasets = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                            return acc + dataset.data[tooltipItems[0].dataIndex];
                        }, 0);

                        const totalPositive = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                          const value = dataset.data[tooltipItems[0].dataIndex];
                          return value > 0 ? acc + value : acc;
                        }, 0);

                        const totalNegative = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                          const value = dataset.data[tooltipItems[0].dataIndex];
                          return value < 0 ? acc + value : acc;
                        }, 0);

                        return [
                            'Totaal Uitgaven: ' + formatCurrency(totalNegative),
                            'Totaal Inkomen: ' + formatCurrency(totalPositive),
                            'Totaal Alle Categorieën: ' + formatCurrency(totalAllDatasets)
                        ];
                    }
                }
            }
        }
    }
});

document.getElementById("togglePeriod").addEventListener("click", function() {
    isYearly = !isYearly;
    this.textContent = isYearly ? "Toon Maandoverzicht" : "Toon Jaaroverzicht";
    updateInkomenChart(isYearly);
});

function updateInkomenChart(isYearly) {
    const url = isYearly ? "/get_yearly_inkomen_data" : "/get_monthly_inkomen_data";
    fetch(url)
        .then(response => response.json())
        .then(data => {
            inkomenChart.data.labels = data.labels;
            inkomenChart.data.datasets = [
                ...data.datasets,
                {
                    label: "12-maanden Gemiddelde",
                    data: data.avg_data,
                    type: "line",
                    borderColor: redColor,
                    backgroundColor: "rgba(255,45,85,0.2)",
                    fill: false,
                    tension: 0.1
                }
            ];
            inkomenChart.update();
        });
}

// 4. Top 10 Omschrijvingen (horizontal bar)
const top10Labels = getJSONData("top10Labels");
const top10Data = getJSONData("top10Data");
const ctxTop10 = document.getElementById("top10Chart").getContext("2d");
new Chart(ctxTop10, {
    type: "bar",
    data: {
        labels: top10Labels,
        datasets: [{
            label: "Uitgaven (EUR)",
            data: top10Data,
            backgroundColor: redColor
        }]
    },
    options: {
        indexAxis: "y",   // <-- horizontaal
        responsive: true,
        scales: {
            x: { ticks: { color: "#f4f4f4" } },
            y: { ticks: { color: "#f4f4f4" } }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return formatCurrency(tooltipItem.raw);
                    }
                }
            }
        }
    }
});

// 5. Categorieën per jaar (stacked bar chart)
const categorieenJaarLabels = getJSONData("categorieenJaarLabels");
const categorieenJaarDatasets = getJSONData("categorieenJaarDatasets");
const ctxCategorieenJaar = document.getElementById("categorieenJaarChart").getContext("2d");
new Chart(ctxCategorieenJaar, {
    type: "bar",
    data: {
        labels: categorieenJaarLabels,
        datasets: categorieenJaarDatasets.map((dataset, index) => ({
            ...dataset,
            backgroundColor: colorVariants[index % colorVariants.length]
        }))
    },
    options: {
        responsive: true,
        scales: {
            x: { ticks: { color: "#f4f4f4" },
                 stacked: true 
            },
            y: { 
                ticks: { color: "#f4f4f4" },
                stacked: true
            }
        },
        plugins: {
            tooltip: {
                callbacks: {
                    label: function(tooltipItem) {
                        return formatCurrency(tooltipItem.raw);
                    },
                    footer: (tooltipItems) => {
                        const totalAllDatasets = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                            return acc + dataset.data[tooltipItems[0].dataIndex];
                        }, 0);

                        const totalPositive = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                          const value = dataset.data[tooltipItems[0].dataIndex];
                          return value > 0 ? acc + value : acc;
                        }, 0);

                        const totalNegative = tooltipItems[0].chart.data.datasets.reduce((acc, dataset) => {
                          const value = dataset.data[tooltipItems[0].dataIndex];
                          return value < 0 ? acc + value : acc;
                        }, 0);

                        return [
                            'Totaal Uitgaven: ' + formatCurrency(totalNegative),
                            'Totaal Inkomen: ' + formatCurrency(totalPositive),
                            'Totaal Alle Categorieën: ' + formatCurrency(totalAllDatasets)
                        ];
                    }
                }
            }
        }
    }
});

// 6. Saldi van de lopende rekening en de spaarrekening
// Verwijder deze code omdat de saldi al in de HTML worden weergegeven
// const lopendeRekeningSaldo = getJSONData("lopendeRekeningSaldo");
// const spaarrekeningSaldo = getJSONData("spaarrekeningSaldo");

// document.getElementById("lopendeRekeningSaldo").textContent = formatCurrency(lopendeRekeningSaldo);
// document.getElementById("spaarrekeningSaldo").textContent = formatCurrency(spaarrekeningSaldo);