# SEM Campaign Generator

A Python-based tool to **automatically generate SEM (Search Engine Marketing) campaigns** from a configuration file, keyword ideas, and filtering logic.  
The tool builds **search ad groups, Performance Max themes, and shopping recommendations**, exporting them into an Excel file ready for Google Ads.

---

## 📌 Features
- Load campaign settings from a simple YAML config
- Generate keywords based on brand, competitors, and categories
- Apply filters for:
  - Search volume
  - Max CPC
  - Relevance
- Build structured campaign outputs:
  - Search campaign ad groups
  - Performance Max themes
  - Shopping bid recommendations
- Export all results to Excel

---

## 📂 Project Structure
```

sem\_campaign\_generator/
│
├── config.yaml                # Configuration file
├── main.py                    # Main entry point
├── requirements.txt           # Python dependencies
├── src/                       # Source code
│   ├── keyword\_generator.py
│   ├── data\_processor.py
│   ├── campaign\_builder.py
│   ├── exporter.py
│   ├── utils.py
│
└── output/                    # Generated campaign files

````

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/vijayshreepathak/Sem_campaign_generator.git
   cd Sem_campaign_generator
````

2. **Set up a virtual environment**

   ```bash
   python -m venv venv
   # Activate:
   # Mac/Linux:
   source venv/bin/activate
   # Windows (PowerShell):
   venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

---

## 📝 Configuration (`config.yaml`)

Below is an **example config** for **Nutrabay** as a brand and **BigMuscles Nutrition** as a competitor.
📌 *You can replace them with **any website or brand names** based on your usage.*

```yaml
brand:
  url: "https://www.nutrabay.com"   # Replace with your brand's website
  name: "Nutrabay"                  # Replace with your brand name
  
competitor:
  url: "https://www.bigmusclesnutrition.com"   # Replace with competitor's website
  name: "BigMuscles Nutrition"                 # Replace with competitor name

filters:
  min_volume: 50
  max_cpc: 2.0
  excluded_keywords:
    - free
    - jobs
    - cheap
```

---

## 🖥 System Design Diagram

> GitHub supports Mermaid diagrams in README files. If your viewer doesn't show it, view the README directly on GitHub.

```mermaid
flowchart TD
    subgraph User_Inputs
        A[config.yaml]
    end

    subgraph Processing
        B[Main Script: main.py]
        C[Keyword Generator]
        D[Data Processor]
        E[Campaign Builder]
    end

    subgraph Output
        F[Exporter]
        G[Excel/CSV Output]
    end

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G

    style A fill:#e1f5fe,stroke:#333,stroke-width:1px
    style B fill:#f3e5f5,stroke:#333,stroke-width:1px
    style C fill:#f3e5f5,stroke:#333,stroke-width:1px
    style D fill:#f3e5f5,stroke:#333,stroke-width:1px
    style E fill:#f3e5f5,stroke:#333,stroke-width:1px
    style F fill:#e8f5e8,stroke:#333,stroke-width:1px
    style G fill:#e8f5e8,stroke:#333,stroke-width:1px
```

**How it works:**

1. **Config File** — Defines brand, competitor, filters, and campaign rules.
2. **Keyword Generator** — Expands seed terms and fetches related keywords.
3. **Data Processor** — Cleans, filters, and applies constraints.
4. **Campaign Builder** — Structures search, PMax, and shopping campaigns.
5. **Exporter** — Saves results into Excel/CSV files in `/output`.

---

## ▶️ Running the Tool

### Basic Run

```bash
python main.py
```

### Run with Custom Config and Verbose Output

```bash
python main.py --config config.yaml --verbose
```

---

## 📊 Example Output

After running, the tool will produce:

* **Search Campaign Ad Groups** (`search_adgroups.xlsx`)
* **Performance Max Themes**
* **Shopping Campaign Recommendations**

All stored in the `/output` directory.

---

## 🚀 Customization

* Replace the `brand` and `competitor` URLs/names in `config.yaml` to match your business.
* Adjust `filters` to fine-tune keyword selection.
* Add/remove keyword categories in `keyword_generator.py` to suit your niche.

---

## 🛠 Dependencies

* Python 3.8+
* pandas
* openpyxl
* scikit-learn
* pyyaml
* tqdm

(Install via `pip install -r requirements.txt`)

---

## 📄 License

MIT License.
Free for personal and commercial use — attribution appreciated.

---

## ✨ Author

**Vijayshree Vaibhav** (Ex-Snapchat, Cube)

---

```

---
- Also produce a PNG export of the Mermaid diagram (if you prefer an image fallback for viewers that don't render Mermaid). Which would you like next?
```
