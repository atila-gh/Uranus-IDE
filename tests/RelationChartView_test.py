class FeatureExtractor:
    class_variable = "global_feature"

    def __init__(self, name):
        self.name = name
        self.features = []

    def analyze(self, data):
        self.data = data  # instance variable
        local_result = []  # local variable

        def parse():
            self.parsed = True  # instance variable in nested function
            temp = "parsing..."  # local variable in nested function

            def tokenize():
                self.tokens = ["token1", "token2"]  # instance variable in deeper nested function
                token_temp = len(self.tokens)  # local variable in deeper nested function

                def summarize():
                    self.summary = f"{self.name} has {token_temp} tokens"  # instance variable
                    summary_temp = "done"  # local variable
                    return self.summary

                return summarize()

            return tokenize()

        result = parse()
        local_result.append(result)
        return local_result

    def report(self):
        self.report_data = {
            "name": self.name,
            "features": self.features,
            "summary": getattr(self, "summary", None)
        }
        return self.report_data
    
    
    
class AdvancedFeatureExtractor(FeatureExtractor):
    version = "2.0"  # class variable

    def __init__(self, name, level):
        super().__init__(name)
        self.level = level  # new instance variable
        self.advanced_features = []

    def analyze(self, data):
        # استفاده از متد پایه و افزودن رفتار جدید
        base_result = super().analyze(data)
        self.advanced_features.append(f"Level-{self.level}")
        local_flag = True  # local variable

        def refine():
            self.refined = True  # instance variable
            refine_temp = "refining..."  # local variable

            def deep_refine():
                self.deep_data = [f"{d}-refined" for d in data]  # instance variable
                deep_temp = len(self.deep_data)  # local variable

                def finalize():
                    self.final_result = f"{self.name} refined {deep_temp} items"
                    final_temp = "complete"  # local variable
                    return self.final_result

                return finalize()

            return deep_refine()

        advanced_result = refine()
        return base_result + [advanced_result]

    def export(self):
        self.export_data = {
            "name": self.name,
            "level": self.level,
            "features": self.features,
            "advanced": self.advanced_features,
            "summary": getattr(self, "summary", None),
            "final": getattr(self, "final_result", None)
        }
        return self.export_data
    
    
class FeatureAnalyzer:
    category = "analysis"  # class variable

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.extractor = FeatureExtractor(name)  # composition
        self.analysis_result = []

    def process(self):
        self.extractor.analyze(self.data)  # استفاده از متد کلاس دیگر
        self.analysis_result.append("initial processed")
        local_flag = True

        def evaluate():
            self.evaluated = True
            eval_temp = "evaluating..."

            def correlate():
                self.correlation = {
                    "length": len(self.data),
                    "tokens": getattr(self.extractor, "tokens", [])
                }
                corr_temp = "correlation done"

                def finalize():
                    self.final_output = {
                        "name": self.name,
                        "summary": getattr(self.extractor, "summary", None),
                        "correlation": self.correlation
                    }
                    final_temp = "finalized"
                    return self.final_output

                return finalize()

            return correlate()

        result = evaluate()
        self.analysis_result.append(result)
        return self.analysis_result

    def show(self):
        return {
            "analyzer": self.name,
            "category": self.category,
            "evaluated": getattr(self, "evaluated", False),
            "final_output": getattr(self, "final_output", None)
        }