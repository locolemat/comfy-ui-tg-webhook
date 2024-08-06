from localisation import language

class GenModel:
    def __init__(self, name, name_text, desc_text):
        self.name = name
        self.name_text = name_text
        self.desc_text = desc_text
        self.gen_type = None

    
    def get_button_callback(self):
        return f'{self.gen_type}:{self.name}'

    
class ImgModel(GenModel):
    def __init__(self, name, name_text, desc_text):
        super().__init__(name=name, name_text=name_text, desc_text=desc_text)
        self.gen_type = "model:"


class VideoModel(GenModel):
    def __init__(self, name, name_text, desc_text):
        super().__init__(name=name, name_text=name_text, desc_text=desc_text)
        self.gen_type = "v_model:"


model_anithing = ImgModel(name="anithing_v11Pruned.safetensors", name_text=language.model_anithing, desc_text=language.model_anithing_desc)
model_dreamshaper= ImgModel(name="dreamshaper_8.safetensors", name_text=language.model_dreamshaper, desc_text=language.model_dreamshaper_desc)
model_epicrealism = ImgModel(name="epicrealism_naturalSinRC1VAE.safetensors", name_text=language.model_epicrealism, desc_text=language.model_epicrealism_desc)
model_photon = ImgModel(name="photon_v1.safetensors", name_text=language.model_photon, desc_text=language.model_photon_desc)
model_realisticvision = ImgModel(name="realisticVisionV60B1_v51HyperVAE.safetensors", name_text=language.model_realisticvision, desc_text=language.model_realisticvision_desc)

svd = VideoModel(name="SVD/svd.safetensors", name_text=language.v_model_svd, desc_text=language.v_model_svd_desc)
svd_xt = VideoModel(name="SVD/svd_xt.safetensors", name_text=language.v_model_svd_xt, desc_text=language.v_model_svd_xt_desc)

image_models = [model_anithing, model_dreamshaper, model_epicrealism, model_photon, model_realisticvision]
video_models = [svd, svd_xt]