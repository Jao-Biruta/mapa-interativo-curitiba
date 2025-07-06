import pygame
import sys
import math
import random
import os # Importa a biblioteca 'os' para lidar com caminhos de ficheiros
import pygame.gfxdraw # Importa a biblioteca para desenho com anti-aliasing

# --- FUNÇÃO AUXILIAR PARA LIDAR COM OS CAMINHOS DOS FICHEIROS ---
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para o PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Usa a localização do ficheiro do script como base
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)

# --- Configurações Iniciais ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 720
BACKGROUND_COLOR = (222, 220, 214) # Cor de fundo cinza claro, similar à da imagem
FOG_COLOR_FALLBACK = (222, 220, 214, 240) # Cor sólida da névoa caso a imagem falhe
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)
POI_ICON_SIZE = (64, 64) # Tamanho padrão para os ícones no mapa

# --- Caminhos dos ficheiros agora incluem a pasta 'assets' ---
ASSETS_FOLDER = 'assets'
FONT_REGULAR_FILE = os.path.join(ASSETS_FOLDER, 'Rubik-Regular.ttf')
FONT_TITLE_FILE = os.path.join(ASSETS_FOLDER, 'Rubik-Black.ttf')
ICON_FILE = os.path.join(ASSETS_FOLDER, 'icone-araucaria.png')
MAP_FILE = os.path.join(ASSETS_FOLDER, 'mapa_curitiba.png')
FOG_IMAGE_FILE = os.path.join(ASSETS_FOLDER, 'fog.png') 


# --- Evento Personalizado para Revelar a Névoa ---
REVEAL_EVENT = pygame.USEREVENT + 1


# --- Classe de Animação para Revelar a Névoa ---
class RevealAnimation:
    def __init__(self, fog_surface, map_pos, final_radius, duration=399):
        self.fog_surface = fog_surface
        self.map_pos = map_pos
        self.final_radius = final_radius
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        self.is_finished = False

    def update(self):
        if self.is_finished:
            return False
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            x, y, r = int(self.map_pos.x), int(self.map_pos.y), int(self.final_radius)
            pygame.gfxdraw.filled_circle(self.fog_surface, x, y, r, (0,0,0,0))
            pygame.gfxdraw.aacircle(self.fog_surface, x, y, r, (0,0,0,0))
            self.is_finished = True
            return True
        else:
            t = elapsed / self.duration
            eased_t = 1 - pow(1 - t, 3)
            current_radius = int(self.final_radius * eased_t)
            x, y = int(self.map_pos.x), int(self.map_pos.y)
            
            pygame.gfxdraw.filled_circle(self.fog_surface, x, y, current_radius, (0,0,0,0))
            pygame.gfxdraw.aacircle(self.fog_surface, x, y, current_radius, (0,0,0,0))
            return True


# --- Dados dos Pontos Turísticos (Exemplos) ---
PONTOS_TURISTICOS_DATA = [
    { "id": "praca_tiradentes", "nome": "Praça Tiradentes", "pos": (8935, 5691), "descricao": "Localizada no coração do centro histórico de Curitiba, a Praça Tiradentes é um marco da cidade. É cercada por importantes edifícios históricos e é um ponto de encontro popular para eventos culturais e sociais. É a principal de Curitiba, dominada pela Catedral Basílica Menor de Nossa Senhora da Luz, centenária em 1993. Nesta região, em 29 de março de 1693, foi fundada Curitiba. Antigamente conhecida como Largo da Matriz, a praça é o marco zero da cidade. Em 1880, em função da visita do Imperador Pedro II ao Paraná, o Largo passou a se chamar D. Pedro II. Nove anos mais tarde, com a Proclamação da República, recebeu o nome atual de Praça Tiradentes. É um importante terminal de transporte coletivo.", "imagem_path": "" },
    { "id": "rua_flores", "nome": "Rua das Flores", "pos": (9119, 5683), "descricao": "A Rua das Flores é uma charmosa rua de pedestres no centro de Curitiba, famosa por suas flores e árvores. É um ótimo lugar para passear, fazer compras e apreciar a arquitetura local.", "imagem_path": "" },
    { "id": "rua_24_horas", "nome": "Rua 24 Horas", "pos": (8760, 5904), "descricao": "Uma rua coberta que funciona 24 horas por dia, oferecendo uma variedade de lojas, restaurantes e cafés. É um local popular tanto para moradores quanto para turistas.", "imagem_path": "" },
    { "id": "museu_ferroviario", "nome": "Museu Ferroviário", "pos": (9178, 6029), "descricao": "O Museu Ferroviário de Curitiba é dedicado à história das ferrovias no Brasil. O museu abriga uma coleção de locomotivas, vagões e outros artefatos ferroviários, além de exposições sobre a história do transporte ferroviário.", "imagem_path": ""},
    { "id": "teatro_paiol", "nome": "Teatro Paiol", "pos": (9481, 6451), "descricao": "Localizado em um antigo paiol de pólvora, o Teatro Paiol é um espaço cultural que abriga peças de teatro, shows e eventos culturais. É conhecido por sua acústica excepcional e ambiente intimista.", "imagem_path": "" },
    { "id": "jardim_botanico", "nome": "Jardim Botânico", "pos": (10225, 6227), "descricao": "O Jardim Botânico de Curitiba, inaugurado em 1991, é um dos principais pontos turísticos da cidade. A sua estufa de metal e vidro, inspirada no Palácio de Cristal de Londres, é o seu marco mais famoso e abriga espécies botânicas da Floresta Atlântica.", "imagem_path": "" },
    { "id": "mercado_municipal", "nome": "Mercado Municipal", "pos": (9503, 5909), "descricao": "O Mercado Municipal de Curitiba é um local vibrante onde você pode encontrar uma variedade de produtos frescos, especiarias, artesanato e comidas típicas. É um ótimo lugar para experimentar a culinária local e comprar lembranças.", "imagem_path": "" },
    { "id": "teatro_guaira", "nome": "Teatro Guaíra", "pos": (9190, 5637), "descricao": "Um dos principais teatros do Brasil, o Teatro Guaíra é conhecido por sua arquitetura imponente e por abrigar uma variedade de eventos culturais, incluindo óperas, balés e concertos. É um símbolo da vida cultural de Curitiba.", "imagem_path": "" },
    { "id": "palacio_liberdade", "nome": "Paço da Liberdade", "pos": (9010, 5701), "descricao": "O Palácio da Liberdade é a sede do governo do estado do Paraná. Sua arquitetura neoclássica e os jardins bem cuidados fazem dele um local de visitação popular, especialmente durante eventos culturais e exposições.", "imagem_path": "" },
    { "id": "passeio_publico", "nome": "Passeio Público", "pos": (9108, 5512), "descricao": "O Passeio Público é um dos parques mais antigos de Curitiba, inaugurado em 1886. É um espaço verde com lagos, pontes e áreas para piqueniques, ideal para relaxar e apreciar a natureza no coração da cidade.", "imagem_path": "" },
    { "id": "centro_civico", "nome": "Centro Cívico", "pos": (9048, 5169), "descricao": "O Centro Cívico é o coração político de Curitiba, onde estão localizados o Palácio Iguaçu, a Assembleia Legislativa e outros edifícios governamentais. É um local importante para eventos cívicos e manifestações.", "imagem_path": "" },
    { "id": "museu_olho", "nome": "Museu Oscar Niemeyer", "pos": (9111, 4876), "descricao": "Popularmente conhecido como Museu do Olho, devido ao design de sua torre, é um espaço dedicado à exposição de Artes Visuais, Arquitetura e Design. Projetado por Oscar Niemeyer, é um dos maiores complexos de exposição da América Latina.", "imagem_path": "" },     
    { "id": "bosque_papa", "nome": "Bosque do Papa", "pos": (9000, 4792), "descricao": "Um parque dedicado ao Papa João Paulo II, com uma trilha de caminhada, lago e áreas para piqueniques. É um local tranquilo para relaxar e apreciar a natureza, além de abrigar uma réplica da Capela de São Miguel.", "imagem_path": "" },
    { "id": "bosque_alemao", "nome": "Bosque Alemão", "pos": (8332, 4646), "descricao": "Um parque temático que celebra a cultura alemã em Curitiba. Possui uma trilha de caminhada, um mirante e uma réplica de uma casa típica alemã. É um ótimo lugar para aprender sobre a história da imigração alemã na região.", "imagem_path": "" },
    { "id": "universidade_meio_ambiente", "nome": "UNILIVRE", "pos": (8492, 4335), "descricao": "Um espaço educacional dedicado à preservação ambiental e sustentabilidade. Oferece cursos, palestras e atividades voltadas para a conscientização ambiental, além de um belo jardim botânico.", "imagem_path": "" },
    { "id": "parque_lourenco", "nome": "Parque São Lourenço", "pos": (9123, 3710), "descricao": "Um parque urbano com áreas verdes, lago e trilhas para caminhada. É um local popular para atividades ao ar livre, como caminhadas, corridas e piqueniques, além de abrigar eventos culturais e esportivos.", "imagem_path": "" },
    { "id": "opera_arame", "nome": "Ópera de Arame", "pos": (8760, 3816), "descricao": "Com uma estrutura tubular de aço e teto transparente, a Ópera de Arame é um dos espaços de espetáculos mais emblemáticos do Brasil. Foi construída em apenas 75 dias e inaugurada em 1992, em meio a um lago e vegetação nativa.", "imagem_path": "" },
    { "id": "parque_tangua", "nome": "Parque Tanguá", "pos": (8548, 3593), "descricao": "Um parque urbano com lago, cascata e mirante. É um local popular para caminhadas, corridas e piqueniques, além de oferecer vistas panorâmicas da cidade.", "imagem_path": "" },
    { "id": "parque_tingui", "nome": "Parque Tingui", "pos": (7648, 4204), "descricao": "Um parque urbano com áreas verdes, lago e trilhas para caminhada. É um local popular para atividades ao ar livre, como caminhadas, corridas e piqueniques, além de abrigar eventos culturais e esportivos.", "imagem_path": "" },
    { "id": "memorial_ucraniano", "nome": "Memorial Ucraniano", "pos": (7678, 4545), "descricao": "Um espaço cultural dedicado à preservação da cultura ucraniana em Curitiba. O memorial abriga uma capela, um museu e um centro cultural, além de eventos e festivais que celebram a cultura ucraniana.", "imagem_path": "" },
    { "id": "portal_italiano", "nome": "Portal Italiano", "pos": (7747, 5079), "descricao": "Um monumento que celebra a imigração italiana em Curitiba. O portal é uma réplica de uma construção típica italiana e é um local popular para fotos e eventos culturais.", "imagem_path": "" },
    { "id": "santa_felicidade", "nome": "Santa Felicidade", "pos": (6588, 4495), "descricao": "Um bairro tradicional de Curitiba, conhecido por sua forte influência italiana. É famoso por seus restaurantes, vinícolas e lojas de artesanato, além de ser um ótimo lugar para experimentar a culinária italiana.", "imagem_path": "" },
    { "id": "parque_barigui", "nome": "Parque Barigui", "pos": (7605, 5549), "descricao": "Um dos maiores parques urbanos de Curitiba, o Parque Barigui é um local popular para caminhadas, corridas e piqueniques. Possui um lago, áreas verdes e uma pista de caminhada ao redor do parque.", "imagem_path": "" },
    { "id": "torre_panoramica", "nome": "Torre Panorâmica", "pos": (8099, 5482), "descricao": "Uma torre de observação que oferece vistas panorâmicas da cidade. É um local popular para turistas e moradores, especialmente ao pôr do sol.", "imagem_path": "" },
    { "id": "centro_historico", "nome": "Centro Histórico", "pos": (8930, 5590), "descricao": "O Centro Histórico de Curitiba é uma área que preserva a arquitetura colonial e a história da cidade. É um local popular para passeios a pé, com várias lojas, restaurantes e museus.", "imagem_path": "" },
]


# --- Classe para o Ponto Turístico (POI) ---
class POI(pygame.sprite.Sprite):
    def __init__(self, data, index, outline_img, fill_img, is_initial=False):
        super().__init__()
        self.id = data["id"]
        self.nome = data["nome"]
        self.map_pos = pygame.math.Vector2(data["pos"])
        self.descricao = data["descricao"]
        self.imagem_path = data["imagem_path"]
        self.index = index
        
        self.outline_img = outline_img
        self.fill_img_original = fill_img
        
        if self.outline_img:
            self.image = self.outline_img.copy()
            self.rect = self.image.get_rect()
            self.use_custom_icon = True
        else:
            self.use_custom_icon = False
            self.radius = 15
            self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

        self.is_visible = is_initial
        self.is_completed = False
        self.is_shaking = False
        self.shake_start_time = 0
        self.shake_duration = 700
        self.shake_magnitude = 0
        
        self.fill_color = GOLD

    def update(self, screen_pos):
        current_time = pygame.time.get_ticks()
        if self.is_shaking:
            elapsed_time = current_time - self.shake_start_time
            if elapsed_time < self.shake_duration:
                self.shake_magnitude = (elapsed_time / self.shake_duration) * 10
                offset_x = random.uniform(-self.shake_magnitude, self.shake_magnitude)
                self.rect.center = (screen_pos[0] + offset_x, screen_pos[1])
            else:
                self.is_shaking = False
                self.shake_magnitude = 0
                self.is_completed = True
                self.fill_color = WHITE 
                self.rect.center = screen_pos
                reveal_event = pygame.event.Event(REVEAL_EVENT, {"pos": self.map_pos, "index": self.index})
                pygame.event.post(reveal_event)
        else:
             self.rect.center = screen_pos

    def draw(self, surface):
        if self.is_visible:
            if self.use_custom_icon:
                colored_fill = self.fill_img_original.copy()
                colored_fill.fill(self.fill_color, special_flags=pygame.BLEND_RGB_MULT)
                surface.blit(colored_fill, self.rect)
                surface.blit(self.outline_img, self.rect)
            else: 
                center_x, center_y = int(self.rect.centerx), int(self.rect.centery)
                pygame.gfxdraw.filled_circle(surface, center_x, center_y, self.radius, BLACK)
                pygame.gfxdraw.aacircle(surface, center_x, center_y, self.radius, BLACK)
                pygame.gfxdraw.filled_circle(surface, center_x, center_y, self.radius - 2, self.fill_color)
                pygame.gfxdraw.aacircle(surface, center_x, center_y, self.radius - 2, self.fill_color)


    def start_shake_animation(self):
        if not self.is_shaking and not self.is_completed:
            self.is_shaking = True
            self.shake_start_time = pygame.time.get_ticks()

# --- Classe para o Cartão de Informações ---
class InfoCard:
    def __init__(self, poi, title_font, body_font, screen_size):
        self.poi = poi
        self.title_font = title_font
        self.body_font = body_font
        
        self.state = 'appearing'
        self.animation_start_time = pygame.time.get_ticks()
        self.size_anim_duration = 200
        self.fade_anim_duration = 70
        
        self.final_rect = pygame.Rect(0, 0, 500, 550)
        self.base_surface = pygame.Surface(self.final_rect.size, pygame.SRCALPHA).convert_alpha()
        
        self.button_color = GOLD
        self.button_rect_on_card = pygame.Rect(0, 0, 150, 50)
        self.button_rect_on_card.centerx = self.final_rect.width // 2
        self.button_rect_on_card.bottom = self.final_rect.height - 20
        self.button_screen_rect = self.button_rect_on_card.copy()

        self.scroll_y = 0
        self.desc_viewport_rect = pygame.Rect(30, 300, self.final_rect.width - 60, 180)
        self._create_text_surface()

        self.update_position(screen_size)
        self.pre_render_card_content()
    
    def _create_text_surface(self):
        """Cria uma superfície grande com todo o texto da descrição."""
        lines = self.wrap_text(self.poi.descricao, self.body_font, self.desc_viewport_rect.width)
        
        if not lines:
            self.full_text_surface = pygame.Surface((1,1))
            self.max_scroll = 0
            return

        line_height = self.body_font.get_linesize()
        total_height = len(lines) * line_height
        
        self.full_text_surface = pygame.Surface((self.desc_viewport_rect.width, total_height), pygame.SRCALPHA)
        
        y = 0
        for line in lines:
            line_surface = self.body_font.render(line, True, WHITE)
            self.full_text_surface.blit(line_surface, (0, y))
            y += line_height
            
        self.max_scroll = max(0, total_height - self.desc_viewport_rect.height)

    def wrap_text(self, text, font, max_width):
        """Função auxiliar para quebrar o texto em linhas."""
        words = text.split(' ')
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        lines.append(current_line.strip())
        return lines

    def update_position(self, screen_size):
        self.final_rect.center = (screen_size[0] // 2, screen_size[1] // 2)
        self.button_screen_rect.topleft = (self.final_rect.left + self.button_rect_on_card.left, 
                                           self.final_rect.top + self.button_rect_on_card.top)

    def start_disappearing(self):
        if self.state == 'idle':
            self.state = 'disappearing'
            self.animation_start_time = pygame.time.get_ticks()

    def is_finished(self):
        return self.state == 'disappearing' and (pygame.time.get_ticks() - self.animation_start_time > self.size_anim_duration)

    def pre_render_card_content(self):
        card_bg_color = (7, 7, 9)
        pygame.draw.rect(self.base_surface, card_bg_color, self.base_surface.get_rect(), border_radius=30)
        title_text = self.title_font.render(self.poi.nome, True, WHITE)
        title_rect = title_text.get_rect(centerx=self.base_surface.get_width() // 2, top=20)
        self.base_surface.blit(title_text, title_rect)
        try:
            if self.poi.imagem_path:
                image_path = resource_path(os.path.join(ASSETS_FOLDER, self.poi.imagem_path))
                image = pygame.image.load(image_path).convert()
            else:
                raise pygame.error("No image path provided")
        except (pygame.error, FileNotFoundError):
            image = pygame.Surface((400, 200)); image.fill((50, 50, 50))
            img_text = self.body_font.render(f"Imagem de {self.poi.nome}", True, WHITE)
            img_text_rect = img_text.get_rect(center=image.get_rect().center)
            image.blit(img_text, img_text_rect)

        image = pygame.transform.scale(image, (400, 200))
        image_rect = image.get_rect(centerx=self.base_surface.get_width() // 2, top=title_rect.bottom + 15)
        self.base_surface.blit(image, image_rect)

    def handle_scroll(self, event):
        """Processa o scroll da roda do rato para o texto."""
        if self.final_rect.collidepoint(pygame.mouse.get_pos()):
            self.scroll_y -= event.y * 20 # Multiplicador para velocidade do scroll
            self.scroll_y = max(0, min(self.scroll_y, self.max_scroll))

    def update(self, mouse_pos):
        if self.state == 'idle':
            if self.button_screen_rect.collidepoint(mouse_pos):
                self.button_color = WHITE
            else:
                self.button_color = GOLD

    def draw(self, screen):
        elapsed_time = pygame.time.get_ticks() - self.animation_start_time
        
        if self.state == 'appearing':
            size_progress = min(elapsed_time / self.size_anim_duration, 1.0)
            eased_size_progress = 1 - pow(1 - size_progress, 3)
            current_scale = 1.1 - (0.1 * eased_size_progress)
            fade_progress = min(elapsed_time / self.fade_anim_duration, 1.0)
            current_alpha = 255 * fade_progress
            if size_progress >= 1.0:
                self.state = 'idle'
        elif self.state == 'disappearing':
            size_progress = min(elapsed_time / self.size_anim_duration, 1.0)
            eased_size_progress = 1 - pow(1 - size_progress, 3)
            current_scale = 1.0 - (0.1 * eased_size_progress)
            fade_progress = min(elapsed_time / self.fade_anim_duration, 1.0)
            current_alpha = 255 * (1 - fade_progress)
        else: # idle
            current_scale = 1.0
            current_alpha = 255

        current_width = self.final_rect.width * current_scale
        current_height = self.final_rect.height * current_scale
        
        final_surface = self.base_surface.copy()
        
        text_viewport = final_surface.subsurface(self.desc_viewport_rect)
        text_viewport.blit(self.full_text_surface, (0, -self.scroll_y))
        
        pygame.draw.rect(final_surface, self.button_color, self.button_rect_on_card, border_radius=40)
        button_text = self.body_font.render("Concluído", True, BLACK)
        button_text_rect = button_text.get_rect(center=self.button_rect_on_card.center)
        final_surface.blit(button_text, button_text_rect)
        
        final_surface.set_alpha(int(current_alpha))
        
        scaled_surface = pygame.transform.scale(final_surface, (int(current_width), int(current_height)))
        scaled_rect = scaled_surface.get_rect(center=self.final_rect.center)
        screen.blit(scaled_surface, scaled_rect)

# --- Classe Principal do Jogo ---
class Game:
    def __init__(self):
        pygame.init()
        self.screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
        pygame.display.set_caption("Mapa Interativo de Curitiba")
        try:
            icon_path = resource_path(ICON_FILE)
            icon_image = pygame.image.load(icon_path)
            pygame.display.set_icon(icon_image)
        except pygame.error as e:
            print(f"Não foi possível carregar o ícone: {e}")
        self.clock = pygame.time.Clock()
        
        try:
            font_title_path = resource_path(FONT_TITLE_FILE)
            font_regular_path = resource_path(FONT_REGULAR_FILE)
            self.font_card_title = pygame.font.Font(font_title_path, 32)
            self.font_card_body = pygame.font.Font(font_regular_path, 20)
        except pygame.error as e:
            print(f"Erro ao carregar fontes personalizadas: {e}. A usar fontes padrão.")
            self.font_card_title = pygame.font.SysFont('arial', 32, bold=True)
            self.font_card_body = pygame.font.SysFont('arial', 20)

        self._load_poi_icons() 

        try:
            map_path = resource_path(MAP_FILE)
            self.map_image_original = pygame.image.load(map_path).convert()
        except pygame.error as e:
            print(f"Erro: Não foi possível carregar 'mapa_curitiba.png'. {e}")
            self.map_image_original = pygame.Surface((16761, 16910)); self.map_image_original.fill((100,100,100))
        
        self.map_full_rect = self.map_image_original.get_rect()
        
        try:
            fog_path = resource_path(FOG_IMAGE_FILE)
            self.fog_surface = pygame.image.load(fog_path).convert_alpha()
        except pygame.error:
            print(f"Não foi possível carregar '{FOG_IMAGE_FILE}'. A usar névoa sólida de fallback.")
            self.fog_surface = pygame.Surface(self.map_full_rect.size, pygame.SRCALPHA)
            self.fog_surface.fill(FOG_COLOR_FALLBACK)
        
        self.reveal_animations = []
        self.is_dragging = False
        self.clicked_on_poi = None 

        self.camera = pygame.Rect(0, 0, 0, 0)
        self.recalculate_camera_aspect() 

        self.pois = pygame.sprite.Group()
        self.active_card = None
        self._setup_pois()

    def _load_poi_icons(self):
        self.poi_outline_images = {}
        self.poi_fill_images = {}
        print("A carregar ícones dos POIs...")
        for poi_data in PONTOS_TURISTICOS_DATA:
            poi_id = poi_data["id"]
            try:
                outline_path = resource_path(os.path.join(ASSETS_FOLDER, f"{poi_id}_outline.png"))
                fill_path = resource_path(os.path.join(ASSETS_FOLDER, f"{poi_id}_fill.png"))
                outline_img = pygame.image.load(outline_path).convert_alpha()
                fill_img = pygame.image.load(fill_path).convert_alpha()
                self.poi_outline_images[poi_id] = pygame.transform.scale(outline_img, POI_ICON_SIZE)
                self.poi_fill_images[poi_id] = pygame.transform.scale(fill_img, POI_ICON_SIZE)
            except pygame.error:
                print(f"Aviso: Ícone para '{poi_id}' não encontrado. A usar círculo como fallback.")
                self.poi_outline_images[poi_id] = None
                self.poi_fill_images[poi_id] = None

    def recalculate_camera_aspect(self, new_width=None):
        current_center = self.camera.center 
        if new_width is None:
            map_aspect = self.map_full_rect.width / self.map_full_rect.height
            screen_aspect = self.screen_size[0] / self.screen_size[1]
            if screen_aspect > map_aspect:
                new_width = self.map_full_rect.height * screen_aspect
            else:
                new_width = self.map_full_rect.width
        new_height = new_width / (self.screen_size[0] / self.screen_size[1])
        self.camera.size = (new_width, new_height)
        self.camera.center = current_center 
        self.check_camera_bounds()

    def _setup_pois(self):
        for i, poi_data in enumerate(PONTOS_TURISTICOS_DATA):
            is_initial = (i == 0)
            outline_img = self.poi_outline_images.get(poi_data["id"])
            fill_img = self.poi_fill_images.get(poi_data["id"])
            poi_obj = POI(poi_data, i, outline_img, fill_img, is_initial=is_initial)
            self.pois.add(poi_obj)

    def map_to_screen(self, map_pos):
        scale = self.screen_size[0] / self.camera.width
        x = (map_pos.x - self.camera.x) * scale
        y = (map_pos.y - self.camera.y) * scale
        return pygame.math.Vector2(x, y)

    def screen_to_map(self, screen_pos):
        scale = self.camera.width / self.screen_size[0]
        x = screen_pos[0] * scale + self.camera.x
        y = screen_pos[1] * scale + self.camera.y
        return pygame.math.Vector2(x, y)

    def trigger_sequential_reveal(self, completed_index, completed_pos):
        next_poi_to_reveal = None
        all_pois = self.pois.sprites()
        for i in range(len(all_pois)):
            idx_to_check = (completed_index + 1 + i) % len(all_pois)
            poi_to_check = next((p for p in all_pois if p.index == idx_to_check), None)
            if poi_to_check and not poi_to_check.is_completed:
                next_poi_to_reveal = poi_to_check
                break
        if next_poi_to_reveal:
            reveal_radius = completed_pos.distance_to(next_poi_to_reveal.map_pos) + 150
        else:
            reveal_radius = 800
        self.reveal_animations.append(RevealAnimation(self.fog_surface, completed_pos, reveal_radius))
        self.reveal_pois_in_area(completed_pos, reveal_radius)

    def handle_zoom(self, zoom_direction, mouse_pos_tuple):
        mouse_pos = pygame.math.Vector2(mouse_pos_tuple)
        mouse_map_pos = self.screen_to_map(mouse_pos)
        
        if zoom_direction > 0: zoom_factor = 0.8
        else: zoom_factor = 1.25
        
        new_width = self.camera.width * zoom_factor
        min_cam_w = self.map_full_rect.width / 15.0

        map_aspect = self.map_full_rect.width / self.map_full_rect.height
        screen_aspect = self.screen_size[0] / self.screen_size[1]
        if screen_aspect > map_aspect: max_cam_w = self.map_full_rect.height * screen_aspect
        else: max_cam_w = self.map_full_rect.width

        if new_width > max_cam_w: new_width = max_cam_w
        if new_width < min_cam_w: new_width = min_cam_w
            
        self.camera.width = new_width
        self.camera.height = new_width / (self.screen_size[0] / self.screen_size[1])
        new_scale = self.camera.width / self.screen_size[0]
        self.camera.x = mouse_map_pos.x - (mouse_pos.x * new_scale)
        self.camera.y = mouse_map_pos.y - (mouse_pos.y * new_scale)
        self.check_camera_bounds()

    def check_camera_bounds(self):
        if self.camera.width >= self.map_full_rect.width:
            self.camera.centerx = self.map_full_rect.centerx
        else:
            self.camera.left = max(self.camera.left, self.map_full_rect.left)
            self.camera.right = min(self.camera.right, self.map_full_rect.right)
        
        if self.camera.height >= self.map_full_rect.height:
            self.camera.centery = self.map_full_rect.centery
        else:
            self.camera.top = max(self.camera.top, self.map_full_rect.top)
            self.camera.bottom = min(self.camera.bottom, self.map_full_rect.bottom)
    
    def reveal_pois_in_area(self, map_pos, radius):
        reveal_rect = pygame.Rect(map_pos[0] - radius, map_pos[1] - radius, radius*2, radius*2)
        for poi in self.pois:
            if not poi.is_visible and reveal_rect.collidepoint(poi.map_pos):
                poi.is_visible = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type == REVEAL_EVENT:
                self.trigger_sequential_reveal(event.index, event.pos)
            elif event.type == pygame.VIDEORESIZE:
                self.screen_size = (event.w, event.h)
                self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
                self.recalculate_camera_aspect(self.camera.width)
                if self.active_card:
                    self.active_card.update_position(self.screen_size)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.active_card and self.active_card.state == 'idle':
                    if self.active_card.button_screen_rect.collidepoint(event.pos):
                        if not self.active_card.poi.is_completed:
                            self.active_card.poi.start_shake_animation()
                        self.active_card.start_disappearing()
                elif event.button == 1 and not self.active_card:
                    clicked_a_poi = False
                    for poi in self.pois:
                        if poi.is_visible and poi.rect.collidepoint(event.pos):
                            self.clicked_on_poi = poi
                            clicked_a_poi = True
                            break
                    if not clicked_a_poi: self.is_dragging = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.clicked_on_poi:
                        if self.clicked_on_poi.rect.collidepoint(event.pos):
                            self.active_card = InfoCard(self.clicked_on_poi, self.font_card_title, self.font_card_body, self.screen_size)
                    self.is_dragging = False
                    self.clicked_on_poi = None
            elif event.type == pygame.MOUSEMOTION:
                if self.clicked_on_poi and not self.is_dragging:
                    self.is_dragging = True
                    self.clicked_on_poi = None
                if self.is_dragging and not self.active_card:
                    scale = self.camera.width / self.screen_size[0]
                    dx, dy = event.rel
                    self.camera.x -= dx * scale
                    self.camera.y -= dy * scale
                    self.check_camera_bounds()
            elif event.type == pygame.MOUSEWHEEL:
                if self.active_card:
                    self.active_card.handle_scroll(event)
                else:
                    self.handle_zoom(event.y, pygame.mouse.get_pos())

    def update_all(self):
        """Atualiza a lógica de todos os objetos do jogo."""
        if self.active_card:
            self.active_card.update(pygame.mouse.get_pos())
            if self.active_card.is_finished():
                self.active_card = None
            
        any(anim.update() for anim in self.reveal_animations)
        self.reveal_animations = [anim for anim in self.reveal_animations if not anim.is_finished]

        for poi in self.pois:
            if self.camera.collidepoint(poi.map_pos):
                screen_pos = self.map_to_screen(poi.map_pos)
                poi.update(screen_pos)

    def draw_all(self):
        """Desenha todos os elementos do jogo no ecrã."""
        self.screen.fill(BACKGROUND_COLOR)
        
        int_camera_rect = pygame.Rect(int(self.camera.x), int(self.camera.y), int(self.camera.width), int(self.camera.height))
        render_rect = int_camera_rect.clip(self.map_full_rect)

        if render_rect.width > 0 and render_rect.height > 0:
            map_subsurface = self.map_image_original.subsurface(render_rect)
            fog_subsurface = self.fog_surface.subsurface(render_rect)
            
            scale = self.screen_size[0] / self.camera.width
            dest_x = (render_rect.x - self.camera.x) * scale
            dest_y = (render_rect.y - self.camera.y) * scale
            dest_w = render_rect.width * scale
            dest_h = render_rect.height * scale

            map_scaled = pygame.transform.scale(map_subsurface, (int(dest_w), int(dest_h)))
            fog_scaled = pygame.transform.scale(fog_subsurface, (int(dest_w), int(dest_h)))
            
            self.screen.blit(map_scaled, (dest_x, dest_y))
            self.screen.blit(fog_scaled, (dest_x, dest_y))

        for poi in self.pois:
            if self.camera.collidepoint(poi.map_pos):
                poi.draw(self.screen)
        
        if self.active_card: self.active_card.draw(self.screen)

    def run(self):
        while True:
            self.handle_events()
            self.update_all()
            self.draw_all()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Game()
    game.run()
