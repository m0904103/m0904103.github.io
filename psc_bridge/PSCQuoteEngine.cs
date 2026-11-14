using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using System.Threading;
using System.Windows.Forms;
using JDPSCAPQuoteOBJLib;

class PSCQuoteEngine
{
    [STAThread]
    static int Main(string[] args)
    {
        if (args.Length < 2)
        {
            Console.WriteLine("Usage: PSCQuoteEngine.exe <symbols_file> <output_json> [wait_ms]");
            return 1;
        }

        string symbolsFile = args[0];
        string outputJson = args[1];
        int waitMs = args.Length >= 3 ? int.Parse(args[2]) : 3500;

        if (!File.Exists(symbolsFile))
        {
            File.WriteAllText(outputJson, "{\"error\": \"symbols_file not found\"}", Encoding.UTF8);
            return 2;
        }

        string[] rawLines = File.ReadAllLines(symbolsFile, Encoding.UTF8);
        List<string> syms = new List<string>();
        foreach (string line in rawLines)
        {
            string s = line.Trim();
            if (!string.IsNullOrEmpty(s)) syms.Add(s);
        }

        try
        {
            ApplicationJDPSCAPQuote api = new ApplicationJDPSCAPQuote();
            api.Init();
            bool status = api.GetSystemStatus();

            // 批次訂閱（每次最多 50 檔，確保封包穩定不遺漏）
            int batchSize = 50;
            for (int i = 0; i < syms.Count; i += batchSize)
            {
                int count = Math.Min(batchSize, syms.Count - i);
                string batch = string.Join(",", syms.GetRange(i, count).ToArray());
                api.AddSymbols(batch);
            }

            // 等待報價元件完成向金贏島索取最新行情快照
            DateTime start = DateTime.Now;
            while ((DateTime.Now - start).TotalMilliseconds < waitMs)
            {
                Application.DoEvents();
                Thread.Sleep(50);
            }

            StringBuilder sb = new StringBuilder();
            sb.AppendLine("{");
            sb.AppendLine("  \"timestamp\": \"" + DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss") + "\",");
            sb.AppendLine("  \"system_status\": " + (status ? "true" : "false") + ",");
            sb.AppendLine("  \"quotes\": [");

            bool first = true;
            foreach (string sym in syms)
            {
                try
                {
                    object qObj = api.GetQuote(sym);
                    object[] q = qObj as object[];
                    if (q != null && q.Length >= 55)
                    {
                        int dp = 2;
                        int.TryParse(Convert.ToString(q[53]), out dp);
                        double div = Math.Pow(10, dp);

                        double preClose = Convert.ToDouble(q[1]) / div;
                        double openP = Convert.ToDouble(q[5]) / div;
                        double highP = Convert.ToDouble(q[6]) / div;
                        double lowP = Convert.ToDouble(q[7]) / div;
                        double bid1 = Convert.ToDouble(q[8]) / div;
                        double ask1 = Convert.ToDouble(q[18]) / div;
                        double avgP = Convert.ToDouble(q[31]) / div;
                        double price = Convert.ToDouble(q[34]) / div;

                        long bid1Size = Convert.ToInt64(q[13]);
                        long ask1Size = Convert.ToInt64(q[23]);
                        long inSize = Convert.ToInt64(q[28]);
                        long outSize = Convert.ToInt64(q[29]);
                        long totalVol = Convert.ToInt64(q[39]);
                        string tradeDate = Convert.ToString(q[0]);

                        if (!first) sb.AppendLine(",");
                        first = false;

                        sb.Append("    {");
                        sb.Append("\"symbol\": \"" + sym + "\", ");
                        sb.Append("\"date\": \"" + tradeDate + "\", ");
                        sb.Append("\"price\": " + price.ToString("F4") + ", ");
                        sb.Append("\"pre_close\": " + preClose.ToString("F4") + ", ");
                        sb.Append("\"open\": " + openP.ToString("F4") + ", ");
                        sb.Append("\"high\": " + highP.ToString("F4") + ", ");
                        sb.Append("\"low\": " + lowP.ToString("F4") + ", ");
                        sb.Append("\"avg_price\": " + avgP.ToString("F4") + ", ");
                        sb.Append("\"bid1\": " + bid1.ToString("F4") + ", ");
                        sb.Append("\"ask1\": " + ask1.ToString("F4") + ", ");
                        sb.Append("\"bid1_size\": " + bid1Size + ", ");
                        sb.Append("\"ask1_size\": " + ask1Size + ", ");
                        sb.Append("\"in_size\": " + inSize + ", ");
                        sb.Append("\"out_size\": " + outSize + ", ");
                        sb.Append("\"total_vol\": " + totalVol);
                        sb.Append("}");
                    }
                }
                catch { }
            }

            sb.AppendLine();
            sb.AppendLine("  ]");
            sb.AppendLine("}");

            File.WriteAllText(outputJson, sb.ToString(), Encoding.UTF8);
            return 0;
        }
        catch (Exception ex)
        {
            File.WriteAllText(outputJson, "{\"error\": \"" + ex.Message.Replace("\"", "\\\"").Replace("\r", " ").Replace("\n", " ") + "\"}", Encoding.UTF8);
            return 3;
        }
    }
}
