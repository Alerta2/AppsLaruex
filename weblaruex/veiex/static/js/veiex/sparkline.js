function LoadSparkline() {
    // Metric
    $('.js-report-sparkline').each(function (sparklineId) {
        var th = $(this)

        // Instead of splitting with "," we are passing the data in JSON format
        // Because splitting may cause getting datas as string
        // And that breaks scale calculators
        // Also this chain clears the HTML content
        data = $.parseJSON(
            th.data("sparkline-data", th.text())
                .text('')
                .data("sparkline-data")
        ),

            // Get width and height of the container
            w = th.width(),
            h = th.height(),

            // Setting the margins
            // You may set different margins for X/Y
            xMargin = 30,
            yMargin = 15,

            // Scale functions
            // Setting the range with the margin
            y = d3.scale.linear()
                .domain([d3.min(data), d3.max(data)])
                .range([yMargin, h - yMargin]),
            x = d3.scale.linear()
                .domain([0, data.length - 1])
                .range([xMargin, w - xMargin]),

            // Scale functions for creating the gradient fill/stroke
            // Calculating the color according to data in the range of colors
            // That user has passed with the data-range-[high-low]-color attributes
            gradientY = d3.scale.linear()
                .domain([d3.min(data), d3.max(data)])
                .range([th.data("range-low-color"), th.data("range-high-color")]),

            // This is a different margin than the one for the chart
            // Setting the gradient stops from 0% to 100% will cause wrong color ranges
            // Because data points are positioned in the center of containing rect
            percentageMargin = 100 / data.length,
            percentageX = d3.scale.linear()
                .domain([0, data.length - 1])
                .range([percentageMargin, 100 - percentageMargin]),

            // Create S
            container = d3.select(this).append("div"),

            // Create tooltip
            tooltip = container
                .append("div")
                .attr("class", "chart-tooltip"),

            // Create SVG object and set dimensions
            vis = container
                .append("svg:svg")
                .attr("width", w)
                .attr("height", h)

        // Create the group object and set styles for gradient definition
        // Which is about to add in a few lines
        g = vis.append("svg:g")
            .attr("stroke", "url(#sparkline-gradient-" + sparklineId + ")")
            .attr("fill", "url(#sparkline-gradient-" + sparklineId + ")"),

            // Create the line
            // Using cardinal interpolation because we need
            // The line to pass on every point
            line = d3.svg.line()
                .interpolate("cardinal")
                .x(function (d, i) { return x(i); })
                .y(function (d) { return h - y(d); }),

            // Create points
            // We are only creating points for first and last data
            // Because that looks cooler :)
            points = g.selectAll(".point")
                .data(data)
                .enter().append("svg:circle")
                .attr("class", "point")
                .attr("cx", function (d, i) { return x(i) })
                .attr("cy", function (d, i) { return h - y(d) })
                .attr("r", function (d, i) { return (i === (data.length - 1) || i === 0) ? 5 : 0; });

        // Append the line to the group
        g.append("svg:path").attr("d", line(data));

        // Bind calculator functions to tooltip
        th.find(".chart-tooltip").data({
            calcY: y,
            calcX: x
        });

        // Create the gradient effect
        // This is where the magic happens
        // We get datas and create gradient stops with calculated colors
        vis.append("svg:defs")
            .append("svg:linearGradient")
            .attr("id", "sparkline-gradient-" + sparklineId)
            .attr("x1", "0%").attr("y1", "0%").attr("x2", "100%").attr("y2", "0%")
            .attr("gradientUnits", "userSpaceOnUse")
            .selectAll(".gradient-stop")
            .data(data)
            .enter()
            .append("svg:stop").attr('offset', function (d, i) {
                return ((percentageX(i))) + "%";
            }).attr("style", function (d) {
                return "stop-color:" + gradientY(d) + ";stop-opacity:1";
            });

        // Creating invisible rectangles for a better hover interaction
        // Because otherwise user would need to hover to the line or point
        // Which is a terrible experience
        // Creating full height invisible bars and binding mouse events
        // To do some special stuff like showing data or adding classes to
        // The point in the targeted area
        var rect = g.selectAll(".bar-rect")
            .data(data)
            .enter().append("svg:rect")
            .attr("class", "bar-rect")
            .attr("x", function (d, i) { return x(i) - (w / data.length / 2) })
            .attr("y", 0)
            .attr("width", w / data.length)
            .attr("height", h)
            .on("mouseenter", function (d, i) {
                // Calculate left position
                var $tooltip = $(this).closest(".js-report-sparkline").find(".chart-tooltip")
                    .html(formatTooltip(d, i)),
                    tooltipLeft = $tooltip.data("calcX")(i) - ($tooltip.width() / 2),
                    tooltipTop = h - $tooltip.data("calcY")(d) - 40;

                // Position it again
                $tooltip.css({
                    left: tooltipLeft + "px",
                    top: tooltipTop + "px"
                }).show();

                // Add hover class to the targeted point
                $(this).parent().parent().find('.point:eq(' + i + ')').attr('class', 'point hover');
            }).on("mouseleave", function (d, i) {
                var $tooltip = $(this).closest(".js-report-sparkline").find(".chart-tooltip");

                // Hide the tooltip
                $tooltip.hide();

                // Remove hover class from the targeted point
                $(this).parent().parent().find('.point:eq(' + i + ')').attr('class', 'point');
            });

        // Helper function to calculate the HTML content of the tooltip
        // Tooltip may contain any HTML
        function formatTooltip(d, i) {
            return '<div class="title">' + d + '</div>'
        }
    });
}