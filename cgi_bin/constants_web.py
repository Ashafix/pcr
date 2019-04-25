HEADER = """
    Content-Type: text/html\n
    <html><body>
    <p>
    """

END = """
    </p>
    </body></html>
    """

SCRIPT = """<script>function update{0}() {{
                  function createRequest() {{
                    var result = null;
                    if (window.XMLHttpRequest) {{
                        // FireFox, Safari, etc.
                        result = new XMLHttpRequest();
                        if (typeof result.overrideMimeType != "undefined") {{
                            result.overrideMimeType("text/xml"); // Or anything else
                        }}
                    }} else if (window.ActiveXObject) {{
                        // MSIE
                        result = new ActiveXObject("Microsoft.XMLHTTP");
                    }}
                    return result;
                }}

                    var req = createRequest();
                    req.onreadystatechange = function () {{
                        if (req.readyState !== 4) {{
                            return;
                        }}
                        var status = document.getElementById("status{0}");
                        var resp = JSON.parse(req.responseText);
                        status.innerHTML = resp.status;
                        if (resp.status === "finished") {{
                            clearInterval(t{0});
                            status = document.getElementById("result{0}");
                            status.innerHTML = resp.result.replace(/\\n/g, "<br />");
                        }}
                    }};
                    var url = "http://{2}:8003/job_result?run_name={1}.{0}";
                    req.open("GET", url, true);
                    req.send();
                    //return job_status;
                }}
                  var t{0} = setInterval(update{0}, 1000);</script>
                  """

TABLE_ROW = """
<tr>
    <td id="sequence{0}">{1}</td>
    <td id="status{0}">unknown</td>
    <td id="result{0}"><ul class="spinner"></td>
</tr>"""

NOT_PUBLIC = """
<div class="comment">
    <br/>
    Your result will not be public and can only be accessed via the direct link. If you lose this link, you cannot access your results.
    <br/>
</div>
"""

MAX_SEQUENCES = """"
Error: Please don't submit more than 100 sequences at once. Feel free to contact us at maximili.peters@mail.huji.ac.il to discuss further options.
<br/>""""

RESULTS = """
<br/>
<a id="results" target="_blank" href="../cgi-bin/results.py?result={}">
    Your results will be here
</a>
<br/>"""

STATUS = """
<h2>Status of run {}</h2>
<table class="table" id="runname_{0}">
    <thead>
        <tr>
            <th>Sequence</th>
            <th>Status</th>
            <th>Results</th>
        </tr>
    </thead>
<tbody>"""

SCRIPT_RESULTS = """
<script>
    var comments = document.getElementsByClassName("comment");
    var i;
    for (i = 0; i < comments.length; i += 1) {
        comments[i].hidden = true;
    }
    document.getElementById("results").innerHTML = "Your results are here";
</script>
"""