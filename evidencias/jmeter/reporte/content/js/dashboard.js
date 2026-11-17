/*
   Licensed to the Apache Software Foundation (ASF) under one or more
   contributor license agreements.  See the NOTICE file distributed with
   this work for additional information regarding copyright ownership.
   The ASF licenses this file to You under the Apache License, Version 2.0
   (the "License"); you may not use this file except in compliance with
   the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
*/
var showControllersOnly = false;
var seriesFilter = "";
var filtersOnlySampleSeries = true;

/*
 * Add header in statistics table to group metrics by category
 * format
 *
 */
function summaryTableHeader(header) {
    var newRow = header.insertRow(-1);
    newRow.className = "tablesorter-no-sort";
    var cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Requests";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 3;
    cell.innerHTML = "Executions";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 7;
    cell.innerHTML = "Response Times (ms)";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 1;
    cell.innerHTML = "Throughput";
    newRow.appendChild(cell);

    cell = document.createElement('th');
    cell.setAttribute("data-sorter", false);
    cell.colSpan = 2;
    cell.innerHTML = "Network (KB/sec)";
    newRow.appendChild(cell);
}

/*
 * Populates the table identified by id parameter with the specified data and
 * format
 *
 */
function createTable(table, info, formatter, defaultSorts, seriesIndex, headerCreator) {
    var tableRef = table[0];

    // Create header and populate it with data.titles array
    var header = tableRef.createTHead();

    // Call callback is available
    if(headerCreator) {
        headerCreator(header);
    }

    var newRow = header.insertRow(-1);
    for (var index = 0; index < info.titles.length; index++) {
        var cell = document.createElement('th');
        cell.innerHTML = info.titles[index];
        newRow.appendChild(cell);
    }

    var tBody;

    // Create overall body if defined
    if(info.overall){
        tBody = document.createElement('tbody');
        tBody.className = "tablesorter-no-sort";
        tableRef.appendChild(tBody);
        var newRow = tBody.insertRow(-1);
        var data = info.overall.data;
        for(var index=0;index < data.length; index++){
            var cell = newRow.insertCell(-1);
            cell.innerHTML = formatter ? formatter(index, data[index]): data[index];
        }
    }

    // Create regular body
    tBody = document.createElement('tbody');
    tableRef.appendChild(tBody);

    var regexp;
    if(seriesFilter) {
        regexp = new RegExp(seriesFilter, 'i');
    }
    // Populate body with data.items array
    for(var index=0; index < info.items.length; index++){
        var item = info.items[index];
        if((!regexp || filtersOnlySampleSeries && !info.supportsControllersDiscrimination || regexp.test(item.data[seriesIndex]))
                &&
                (!showControllersOnly || !info.supportsControllersDiscrimination || item.isController)){
            if(item.data.length > 0) {
                var newRow = tBody.insertRow(-1);
                for(var col=0; col < item.data.length; col++){
                    var cell = newRow.insertCell(-1);
                    cell.innerHTML = formatter ? formatter(col, item.data[col]) : item.data[col];
                }
            }
        }
    }

    // Add support of columns sort
    table.tablesorter({sortList : defaultSorts});
}

$(document).ready(function() {

    // Customize table sorter default options
    $.extend( $.tablesorter.defaults, {
        theme: 'blue',
        cssInfoBlock: "tablesorter-no-sort",
        widthFixed: true,
        widgets: ['zebra']
    });

    var data = {"OkPercent": 100.0, "KoPercent": 0.0};
    var dataset = [
        {
            "label" : "FAIL",
            "data" : data.KoPercent,
            "color" : "#FF6347"
        },
        {
            "label" : "PASS",
            "data" : data.OkPercent,
            "color" : "#9ACD32"
        }];
    $.plot($("#flot-requests-summary"), dataset, {
        series : {
            pie : {
                show : true,
                radius : 1,
                label : {
                    show : true,
                    radius : 3 / 4,
                    formatter : function(label, series) {
                        return '<div style="font-size:8pt;text-align:center;padding:2px;color:white;">'
                            + label
                            + '<br/>'
                            + Math.round10(series.percent, -2)
                            + '%</div>';
                    },
                    background : {
                        opacity : 0.5,
                        color : '#000'
                    }
                }
            }
        },
        legend : {
            show : true
        }
    });

    // Creates APDEX table
    createTable($("#apdexTable"), {"supportsControllersDiscrimination": true, "overall": {"data": [0.9292857142857143, 500, 1500, "Total"], "isController": false}, "titles": ["Apdex", "T (Toleration threshold)", "F (Frustration threshold)", "Label"], "items": [{"data": [1.0, 500, 1500, "PERF-01 GET listado"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-03 GET formulario"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-01 GET login"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-02 GET formulario"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-02 POST reservación"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-03 GET login"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-03 POST reservación"], "isController": false}, {"data": [0.1, 500, 1500, "PERF-03 POST login"], "isController": false}, {"data": [1.0, 500, 1500, "PERF-02 GET login"], "isController": false}, {"data": [0.5, 500, 1500, "PERF-02 POST login"], "isController": false}, {"data": [0.4, 500, 1500, "PERF-01 POST login"], "isController": false}]}, function(index, item){
        switch(index){
            case 0:
                item = item.toFixed(3);
                break;
            case 1:
            case 2:
                item = formatDuration(item);
                break;
        }
        return item;
    }, [[0, 0]], 3);

    // Create statistics table
    createTable($("#statisticsTable"), {"supportsControllersDiscrimination": true, "overall": {"data": ["Total", 700, 0, 0.0, 238.51000000000013, 5, 2132, 72.0, 1355.9, 1411.8999999999999, 1545.8200000000002, 10.480610869890702, 40.27942349621949, 3.940171620002994], "isController": false}, "titles": ["Label", "#Samples", "FAIL", "Error %", "Average", "Min", "Max", "Median", "90th pct", "95th pct", "99th pct", "Transactions/s", "Received", "Sent"], "items": [{"data": ["PERF-01 GET listado", 250, 0, 0.0, 72.18800000000002, 50, 113, 69.0, 79.9, 81.0, 84.0, 8.725394387826329, 9.415586717332124, 1.968326273035041], "isController": false}, {"data": ["PERF-03 GET formulario", 50, 0, 0.0, 77.86000000000001, 38, 118, 83.0, 104.9, 111.14999999999998, 118.0, 15.832805573147562, 35.62381253958201, 3.664428633628879], "isController": false}, {"data": ["PERF-01 GET login", 50, 0, 0.0, 7.579999999999998, 5, 49, 6.0, 8.899999999999999, 12.349999999999987, 49.0, 1.7067759003242873, 2.4218216632531147, 0.22501440092165897], "isController": false}, {"data": ["PERF-02 GET formulario", 90, 0, 0.0, 32.477777777777774, 30, 45, 32.0, 35.0, 41.0, 45.0, 3.0638297872340425, 6.8936170212765955, 0.7091090425531915], "isController": false}, {"data": ["PERF-02 POST reservación", 90, 0, 0.0, 132.21111111111114, 110, 151, 133.5, 145.0, 146.9, 151.0, 3.0520889853499726, 37.316457383088036, 2.755026938924308], "isController": false}, {"data": ["PERF-03 GET login", 5, 0, 0.0, 31.2, 18, 37, 34.0, 37.0, 37.0, 37.0, 131.57894736842104, 186.70333059210526, 17.34683388157895], "isController": false}, {"data": ["PERF-03 POST reservación", 50, 0, 0.0, 144.17999999999992, 88, 240, 134.0, 219.8, 229.14999999999998, 240.0, 19.21598770176787, 127.75666854823214, 11.289392774788626], "isController": false}, {"data": ["PERF-03 POST login", 5, 0, 0.0, 1741.2, 1432, 2132, 1513.0, 2132.0, 2132.0, 2132.0, 2.3234200743494426, 51.548613934711895, 1.4362547920539033], "isController": false}, {"data": ["PERF-02 GET login", 30, 0, 0.0, 6.033333333333333, 5, 8, 6.0, 6.0, 6.899999999999999, 8.0, 1.0354110581901013, 1.4691916675295091, 0.1365043875543591], "isController": false}, {"data": ["PERF-02 POST login", 30, 0, 0.0, 1356.6333333333334, 1324, 1392, 1355.5, 1383.0, 1387.6, 1392.0, 0.988793671720501, 11.604195420649308, 0.6112367130850362], "isController": false}, {"data": ["PERF-01 POST login", 50, 0, 0.0, 1457.2999999999997, 1382, 1949, 1425.0, 1544.2, 1723.8499999999983, 1949.0, 1.631268147858145, 2.905696388372321, 1.0083913453068416], "isController": false}]}, function(index, item){
        switch(index){
            // Errors pct
            case 3:
                item = item.toFixed(2) + '%';
                break;
            // Mean
            case 4:
            // Mean
            case 7:
            // Median
            case 8:
            // Percentile 1
            case 9:
            // Percentile 2
            case 10:
            // Percentile 3
            case 11:
            // Throughput
            case 12:
            // Kbytes/s
            case 13:
            // Sent Kbytes/s
                item = item.toFixed(2);
                break;
        }
        return item;
    }, [[0, 0]], 0, summaryTableHeader);

    // Create error table
    createTable($("#errorsTable"), {"supportsControllersDiscrimination": false, "titles": ["Type of error", "Number of errors", "% in errors", "% in all samples"], "items": []}, function(index, item){
        switch(index){
            case 2:
            case 3:
                item = item.toFixed(2) + '%';
                break;
        }
        return item;
    }, [[1, 1]]);

        // Create top5 errors by sampler
    createTable($("#top5ErrorsBySamplerTable"), {"supportsControllersDiscrimination": false, "overall": {"data": ["Total", 700, 0, "", "", "", "", "", "", "", "", "", ""], "isController": false}, "titles": ["Sample", "#Samples", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors", "Error", "#Errors"], "items": [{"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}, {"data": [], "isController": false}]}, function(index, item){
        return item;
    }, [[0, 0]], 0);

});
