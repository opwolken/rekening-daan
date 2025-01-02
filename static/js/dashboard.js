function getJSONData(id) {
    const el = document.getElementById(id); 
    return el ? JSON.parse(el.textContent) : null;
}

function formatCurrency(value) {
    return new Intl.NumberFormat('nl-NL', { style: 'currency', currency: 'EUR' }).format(value);
}

const urenLabels = getJSONData("urenLabels");
const urenData = getJSONData("urenData");
Highcharts.chart('urenChart', {
    chart: { type: 'column', backgroundColor: 'transparent' },
    title: { text: null }, // Remove title
    xAxis: { categories: urenLabels, labels: { style: { color: '#f4f4f4' } } },
    yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
    legend: {
        itemStyle: { color: '#f4f4f4' },
        itemHoverStyle: { color: '#f4f4f4' },
        itemHiddenStyle: { color: '#f4f4f4' }
    },
    series: [{
        name: 'Uitgaven per uur',
        data: urenData,
        borderWidth: 0
    }],
    tooltip: {
        style: { color: '#f4f4f4' },
        formatter: function() {
            return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
        }
    }
});

const spaartrendLabels = getJSONData("spaartrendLabels");
const spaartrendData = getJSONData("spaartrendData");
const spaartrendAvgData = getJSONData("spaartrendAvgData");
Highcharts.chart('spaartrendChart', {
    chart: { type: 'line', backgroundColor: 'transparent' },
    title: { text: null }, // Remove title
    xAxis: { categories: spaartrendLabels, labels: { style: { color: '#f4f4f4' } } },
    yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
    legend: {
        itemStyle: { color: '#f4f4f4' },
        itemHoverStyle: { color: '#f4f4f4' },
        itemHiddenStyle: { color: '#f4f4f4' }
    },
    series: [{
        name: 'Cumulatief Sparen',
        data: spaartrendData,
        borderWidth: 0
    }, {
        name: '3-maands Gemiddelde',
        data: spaartrendAvgData,
        borderWidth: 0
    }],
    tooltip: {
        style: { color: '#f4f4f4' },
        formatter: function() {
            return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
        }
    }
});

let isYearly = false;
const inkomenLabels = getJSONData("inkomenLabels");
const inkomenDatasets = getJSONData("inkomenDatasets");
const inkomenAvgData = getJSONData("inkomenAvgData");
Highcharts.chart('inkomenChart', {
    chart: { type: 'column', backgroundColor: 'transparent' },
    title: { text: null }, // Remove title
    xAxis: { categories: inkomenLabels, labels: { style: { color: '#f4f4f4' } } },
    yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
    plotOptions: {
        column: {
            stacking: 'normal'
        }
    },
    legend: {
        itemStyle: { color: '#f4f4f4' },
        itemHoverStyle: { color: '#f4f4f4' },
        itemHiddenStyle: { color: '#f4f4f4' }
    },
    series: inkomenDatasets.map(dataset => ({
        name: dataset.label, // Ensure the series are labeled correctly
        data: dataset.data,
        backgroundColor: dataset.backgroundColor
    })).concat([{
        name: '12-maanden Gemiddelde',
        data: inkomenAvgData,
        type: 'line',
        borderWidth: 0
    }]),
    tooltip: {
        style: { color: '#f4f4f4' },
        formatter: function() {
            return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
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
            Highcharts.chart('inkomenChart', {
                chart: { type: 'column', backgroundColor: 'transparent' },
                title: { text: null }, // Remove title
                xAxis: { categories: data.labels, labels: { style: { color: '#f4f4f4' } } },
                yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
                plotOptions: {
                    column: {
                        stacking: 'normal'
                    }
                },
                legend: {
                    itemStyle: { color: '#f4f4f4' },
                    itemHoverStyle: { color: '#f4f4f4' },
                    itemHiddenStyle: { color: '#f4f4f4' }
                },
                series: data.datasets.map(dataset => ({
                    name: dataset.label, // Ensure the series are labeled correctly
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor
                })).concat([{
                    name: '12-maanden Gemiddelde',
                    data: data.avg_data,
                    type: 'line',
                    borderWidth: 0
                }]),
                tooltip: {
                    style: { color: '#f4f4f4' },
                    formatter: function() {
                        return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
                    }
                }
            });
        });
}

const top10Labels = getJSONData("top10Labels");
const top10Data = getJSONData("top10Data");
Highcharts.chart('top10Chart', {
    chart: { type: 'bar', backgroundColor: 'transparent' },
    title: { text: null }, // Remove title
    xAxis: { categories: top10Labels, labels: { style: { color: '#f4f4f4' } } },
    yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
    legend: {
        itemStyle: { color: '#f4f4f4' },
        itemHoverStyle: { color: '#f4f4f4' },
        itemHiddenStyle: { color: '#f4f4f4' }
    },
    series: [{
        name: 'Uitgaven (EUR)',
        data: top10Data,
        borderWidth: 0
    }],
    tooltip: {
        style: { color: '#f4f4f4' },
        formatter: function() {
            return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
        }
    }
});

const categorieenJaarLabels = getJSONData("categorieenJaarLabels");
const categorieenJaarDatasets = getJSONData("categorieenJaarDatasets");
Highcharts.chart('categorieenJaarChart', {
    chart: { type: 'column', backgroundColor: 'transparent' },
    title: { text: null }, // Remove title
    xAxis: { categories: categorieenJaarLabels, labels: { style: { color: '#f4f4f4' } } },
    yAxis: { title: { text: 'Bedrag (EUR)', style: { color: '#f4f4f4' } }, labels: { style: { color: '#f4f4f4' } } },
    plotOptions: {
        column: {
            stacking: 'normal'
        }
    },
    legend: {
        itemStyle: { color: '#f4f4f4' },
        itemHoverStyle: { color: '#f4f4f4' },
        itemHiddenStyle: { color: '#f4f4f4' }
    },
    series: categorieenJaarDatasets.map(dataset => ({
        name: dataset.label, // Ensure the series are labeled correctly
        data: dataset.data,
        backgroundColor: dataset.backgroundColor
    })),
    tooltip: {
        style: { color: '#f4f4f4' },
        formatter: function() {
            return `<b>${this.x}</b><br/>${this.series.name}: ${formatCurrency(this.y)}`;
        }
    }
});

const sankeyData = getJSONData("sankeyData");
if (sankeyData && sankeyData.length > 0) {
    Highcharts.chart('sankeyChart', {
        chart: { type: 'sankey', backgroundColor: 'transparent' },
        title: { text: null }, // Remove title
        series: [{
            keys: ['from', 'to', 'weight'],
            data: sankeyData,
            name: 'Inkomen naar Uitgaven'
        }],
        tooltip: {
            style: { color: '#f4f4f4' },
            formatter: function() {
                return `<b>${this.point.from} → ${this.point.to}</b><br/>${formatCurrency(this.point.weight)}`;
            }
        }
    });
} else {
    console.error("Sankey data is empty or not correctly formatted.");
}