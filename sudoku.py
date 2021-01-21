import pygame
import pygame.draw
import pygame.gfxdraw

WINDOW_WIDTH = int(1024*1.25)
WINDOW_HEIGHT = int(768*1.25)
BG_COLOR = (0, 64, 100)

class App:
	def __init__(self):
		self.w = WINDOW_WIDTH
		self.h = WINDOW_HEIGHT
		self.running = True
		self.screen = None
		pygame.init()
		pygame.font.init()
		pygame.mouse.set_cursor((8,8),(0,0),(0,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,0)) # hide cursor
		pygame.display.set_caption('Sudoku Solver Visualisation')
		self.screen = pygame.display.set_mode((self.w, self.h))
		self.font = pygame.font.SysFont('Consolas', 44)
		self.animating = False
		self.anim_start_x = 0
		self.anim_end_x = 0
		self.anim_start_y = 0
		self.anim_end_y = 0
		self.progress = 1.0
		self.x = 0
		self.y = 0
		self.src = [0,0]
		self.cursor_x = 0
		self.cursor_y = 0
		self.done = False
		self.paused = False
		self.run()

	def events(self):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.running = False
				return
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					self.running = False
					return
				elif event.key == pygame.K_SPACE:
					self.paused = not self.paused
		
	def get_pos(self, x, y):
		return [self.padx + x * self.divx, self.pady + y * self.divy]

	def animate(self, dt=0):
		if self.progress < 1.0:
			self.progress += dt*20
			dst = self.get_pos(self.cursor_x, self.cursor_y)
			self.x = self.src[0] + (dst[0] - self.src[0]) * self.progress
			self.y = self.src[1] + (dst[1] - self.src[1]) * self.progress
			if self.progress >= 1.0:
				[self.x, self.y] = self.get_pos(self.cursor_x, self.cursor_y)
				return False
			return True
		return False

	def get_row(self):
		row = []
		for i in range(self.cursor_y*9, self.cursor_y*9+9):
			if self.board[i]:
				row.append(self.board[i])
			else:
				row.append(self.tries[i])
		return row

	def get_col(self):
		col = []
		for idx in range(0, 9):
			i = idx * 9 + self.cursor_x
			if self.board[i]:
				col.append(self.board[i])
			else:
				col.append(self.tries[i])
		return col

	def get_square(self):
		square = []
		xs = int(self.cursor_x / 3) * 3
		ys = int(self.cursor_y / 3) * 3
		for i in range(0, 3):
			for j in range(0, 3):
				y = i + ys
				x = j + xs
				idx = x + y * 9
				val = self.board[idx] if self.board[idx] else self.tries[idx]
				square.append(val)
		return square

	def idx(self):
		return self.cursor_y * 9 + self.cursor_x

	def find_number(self, idx):
		found = False
		for i in range(self.tries[idx]+1, 10):
			if i in self.get_row() or i in self.get_col() or i in self.get_square():
				self.tries[idx] = i
				self.try_strings[idx] = self.font.render(str(i), True, [200,0,0])
				return True
			else:
				found = True
				self.tries[idx] = i
				break
		if not found:
			self.tries[idx] = 0
			self.try_strings[idx] = self.font.render('-', True, [200,0,0])
			# find previous try
			for i in range(self.cursor_x - 1 + self.cursor_y * 9, -1, -1):
				if self.tries[i] != 0:
					self.cursor_x = i % 9
					self.cursor_y = int(i / 9)
					return True
		else:
			self.try_strings[idx] = self.font.render(str(self.tries[idx]), True, [200,0,0])
		return False

	def step(self):
		idx = self.idx()
		if self.board[idx] == 0:
			if not self.find_number(idx):
				self.cursor_x += 1
				if self.cursor_x == 9:
					self.cursor_y += 1
					self.cursor_x = 0
					if self.cursor_y == 9:
						self.done = True
						for i in range(0, 81):
							if self.tries[i]:
								self.try_strings[i] = self.font.render(str(self.tries[i]), True, [100,50,190])
		elif self.tries[idx] != 0:
			self.find_number(idx)
		else:
			self.cursor_x += 1
			if self.cursor_x == 9:
				self.cursor_y += 1
				self.cursor_x = 0
				if self.cursor_y == 9:
					self.done = True

		if not self.done:
			self.start_animation()
			

	def start_animation(self):
		self.progress = 0.0
		self.src = [self.x, self.y]

	def run(self):
		self.board = [
			0,0,0, 2,6,0, 7,0,1,
			6,8,0, 0,7,0, 0,9,0,
			1,9,0, 0,0,4, 5,0,0,

			8,2,0, 1,0,0, 0,4,0,
			0,0,4, 6,0,2, 9,0,0,
			0,5,0, 0,0,3, 0,2,8,

			0,0,9, 3,0,0, 0,7,4,
			0,4,0, 0,5,0, 0,3,6,
			7,0,3, 0,1,8, 0,0,0]

		self.tries = [0 for i in self.board]
		self.try_strings = [None for i in self.board]

		text = [self.font.render(str(x), True, [0,0,0]) if x != 0 else None for x in self.board]

		self.padx = 80
		self.pady = 80
		self.divx = (WINDOW_WIDTH - self.padx * 2) / 9
		self.divy = (WINDOW_HEIGHT - self.pady * 2) / 9
		self.maxx = WINDOW_WIDTH - self.padx*2
		self.maxy = WINDOW_HEIGHT - self.pady*2

		[self.x, self.y] = [self.padx, self.pady]

		lines = [
			[self.padx + self.divx * 3-2, self.pady, 5, self.maxy],
			[self.padx + self.divx * 6-2, self.pady, 5, self.maxy],
			[self.padx + self.divx * 3-2, self.pady, 5, self.maxy],
			[self.padx, self.pady + self.divy*3-2, self.maxx, 5],
			[self.padx, self.pady + self.divy*6-2, self.maxx, 5],
		]

		clock = pygame.time.Clock()
		while self.running:
			delta = clock.tick(60)/1000.0
			self.events()
			self.screen.fill(BG_COLOR)
			pygame.gfxdraw.box(self.screen, [self.padx, self.pady, self.maxx, self.maxy], [180,180,180])
			if not self.paused and not self.done and not self.animate(delta):
				self.step()
			for x in range(0, 9):
				for y in range(0, 9):
					i = y * 9 + x
					xp = self.padx + x * self.divx
					yp = self.pady + y * self.divy
					pygame.gfxdraw.rectangle(self.screen, [xp+1, yp+1, self.divx-2, self.divy-2], [40, 40, 40])
					if text[i]:
						clip = text[i].get_clip()
						tx = xp+self.divx/2 - clip.w/2
						ty = yp+self.divy/2 - clip.h/2
						self.screen.blit(text[i], (tx, ty))
					if self.try_strings[i]:
						clip = self.try_strings[i].get_clip()
						tx = xp+self.divx/2 - clip.w/2
						ty = yp+self.divy/2 - clip.h/2
						self.screen.blit(self.try_strings[i], (tx, ty))
			for line in lines:
				pygame.gfxdraw.box(self.screen, line, [50,50,50])
			if not self.done:
				pygame.draw.rect(self.screen, [200, 20, 20], [self.x, self.y, self.divx, self.divy], 3)
			pygame.display.flip()

if __name__ == "__main__":
	App()
